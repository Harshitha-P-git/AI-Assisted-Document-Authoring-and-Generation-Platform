import time
import logging
from typing import Optional, List
from app.core.config import settings

# Lazy import - only import when actually needed (avoids Python 3.14 compatibility issues)
genai = None
openai_client = None

def _get_genai():
    """Lazy import of google.generativeai"""
    global genai
    if genai is None:
        try:
            import google.generativeai as genai_module
            genai = genai_module
        except (ImportError, TypeError, AttributeError) as e:
            error_msg = str(e)
            if "Metaclasses with custom tp_new" in error_msg or "tp_new" in error_msg:
                logger.error("Python 3.14 compatibility issue detected during import. google-generativeai cannot be used.")
            genai = None
        except Exception as e:
            error_msg = str(e)
            if "Metaclasses with custom tp_new" in error_msg or "tp_new" in error_msg:
                logger.error("Python 3.14 compatibility issue detected during import. google-generativeai cannot be used.")
            genai = None
    return genai

def _get_openai():
    """Lazy import of openai"""
    global openai_client
    if openai_client is None:
        try:
            import openai
            openai_client = openai
        except ImportError:
            openai_client = None
        except Exception as e:
            logger.error(f"Error importing openai: {e}")
            openai_client = None
    return openai_client

logger = logging.getLogger(__name__)

# Rate limiting tracking
_rate_limit_times = []


def _check_rate_limit():
    """Check and enforce rate limiting"""
    global _rate_limit_times
    current_time = time.time()
    
    # Remove timestamps older than 1 minute
    _rate_limit_times = [t for t in _rate_limit_times if current_time - t < 60]
    
    if len(_rate_limit_times) >= settings.LLM_RATE_LIMIT_PER_MINUTE:
        raise Exception("Rate limit exceeded. Please try again later.")
    
    _rate_limit_times.append(current_time)


def _generate_with_retry(prompt: str, context: Optional[str] = None) -> str:
    """Generate content with retry logic - tries OpenAI first if enabled, then Gemini, then fallback"""
    full_prompt = prompt
    if context:
        full_prompt = f"Context: {context}\n\n{prompt}"
    
    # Check if we should use mock mode
    if settings.MOCK_LLM:
        logger.info("Using mock LLM mode (MOCK_LLM=true in .env)")
        return _generate_fallback_content(prompt, context)
    
    # Try OpenAI first if enabled (better Python 3.14 compatibility)
    if settings.USE_OPENAI and settings.OPENAI_API_KEY:
        try:
            openai_module = _get_openai()
            if openai_module:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that generates high-quality, informative, and relevant content. Be specific, detailed, and provide actual useful information about the topic."},
                        {"role": "user", "content": full_prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"OpenAI generation failed: {e}, trying Gemini or fallback...")
    
    # Try Gemini API
    try:
        genai_module = _get_genai()
        if not genai_module:
            raise ImportError("google-generativeai not available")
    except Exception as e:
        error_msg = str(e)
        if "Metaclasses with custom tp_new" in error_msg or "tp_new" in error_msg:
            logger.error("Python 3.14 compatibility issue with google-generativeai. Using fallback content.")
            return _generate_fallback_content(prompt, context)
        logger.warning(f"google-generativeai not available: {e}, using fallback content")
        return _generate_fallback_content(prompt, context)
    
    # Initialize Gemini API
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not configured. Set MOCK_LLM=false and provide GEMINI_API_KEY in .env, or use OpenAI with USE_OPENAI=true")
        return _generate_fallback_content(prompt, context)
    
    try:
        genai_module.configure(api_key=settings.GEMINI_API_KEY)
        model = genai_module.GenerativeModel(settings.GEMINI_MODEL)
    except Exception as e:
        error_msg = str(e)
        if "Metaclasses with custom tp_new" in error_msg or "tp_new" in error_msg:
            logger.error("Python 3.14 compatibility issue with google-generativeai. Using fallback content.")
            return _generate_fallback_content(prompt, context)
        raise
    
    for attempt in range(settings.LLM_RETRY_ATTEMPTS):
        try:
            _check_rate_limit()
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "Metaclasses with custom tp_new" in error_msg or "tp_new" in error_msg:
                logger.error("Python 3.14 compatibility issue detected during generation. Using fallback content.")
                return _generate_fallback_content(prompt, context)
            logger.warning(f"LLM generation attempt {attempt + 1} failed: {e}")
            if attempt < settings.LLM_RETRY_ATTEMPTS - 1:
                time.sleep(settings.LLM_RETRY_DELAY * (attempt + 1))
            else:
                logger.error(f"Failed to generate content after {settings.LLM_RETRY_ATTEMPTS} attempts. Using fallback content.")
                return _generate_fallback_content(prompt, context)
    
    # Should not reach here, but just in case
    return _generate_fallback_content(prompt, context)


def _generate_fallback_content(prompt: str, context: Optional[str] = None) -> str:
    """Generate useful fallback content when API is unavailable - context-aware and informative"""
    # Extract section/slide title from prompt - better extraction
    title = ""
    if '"' in prompt:
        parts = prompt.split('"')
        if len(parts) >= 2:
            title = parts[1]
    else:
        # Try to extract from "titled" or "Section Title:" patterns
        if "titled" in prompt.lower():
            parts = prompt.split("titled")
            if len(parts) > 1:
                title = parts[1].split('"')[0].split(":")[0].strip(' "')
        elif "section title:" in prompt.lower():
            title = prompt.split("Section Title:")[-1].strip()
        elif "slide title:" in prompt.lower():
            title = prompt.split("Slide Title:")[-1].strip()
        else:
            # Last resort: get last meaningful part
            title = prompt.split(":")[-1].strip()
    
    # Clean up title
    title = title.strip(' "').strip()
    if not title or len(title) < 2:
        title = "Topic"
    
    title_lower = title.lower()
    
    # Detect content type from context and title - more comprehensive
    is_devotional = False
    is_coffee = False
    is_technical = False
    is_business = False
    is_science = False
    is_health = False
    is_education = False
    
    # Track if context is healthcare-related
    is_healthcare_context = False
    
    if context:
        context_lower = context.lower()
        # Check for healthcare context FIRST (before generic technical)
        if any(word in context_lower for word in ["health", "healthcare", "medical", "patient", "clinical", "hospital", "health care"]):
            is_healthcare_context = True
            # If context mentions healthcare AND title mentions AI/tech/applications, it's AI in healthcare
            if any(word in title_lower for word in ["ai", "artificial intelligence", "machine learning", "technology", "application", "integration", "current", "challenge", "future", "scope", "benefit"]):
                is_technical = True  # Mark as technical (AI in healthcare)
        if any(word in context_lower for word in ["devotional", "shiva", "lord", "devotion", "spiritual", "temple", "prayer"]):
            is_devotional = True
        if any(word in context_lower for word in ["coffee", "espresso", "caffeine", "brew"]):
            is_coffee = True
        if any(word in context_lower for word in ["technical", "technology", "code", "software", "programming"]):
            is_technical = True
        if any(word in context_lower for word in ["business", "corporate", "marketing", "sales", "strategy"]):
            is_business = True
    
    # Detect from title - more comprehensive (check AI/tech FIRST before health)
    if any(word in title_lower for word in ["ai", "artificial intelligence", "machine learning", "ml", "neural", "algorithm", "data science"]):
        is_technical = True  # AI topics are technical
        # If we have healthcare context, this is AI in healthcare
        if is_healthcare_context:
            pass  # Already marked as technical above
    if any(word in title_lower for word in ["shiva", "lord", "devotion", "temple", "prayer", "spiritual", "god", "divine"]):
        is_devotional = True
    if any(word in title_lower for word in ["espresso", "coffee", "caffeine", "brew", "latte", "cappuccino"]):
        is_coffee = True
    if any(word in title_lower for word in ["technical", "technology", "code", "software", "programming", "computer", "digital", "integration", "system", "platform"]):
        is_technical = True
    if any(word in title_lower for word in ["business", "corporate", "marketing", "sales", "strategy", "management"]):
        is_business = True
    if any(word in title_lower for word in ["science", "research", "study", "experiment", "theory"]):
        is_science = True
    # Health detection - only if NOT already technical/AI
    if not is_technical and any(word in title_lower for word in ["health", "medical", "disease", "treatment", "medicine", "healthcare", "patient", "clinical"]):
        is_health = True
    if any(word in title_lower for word in ["education", "learning", "teaching", "student", "school"]):
        is_education = True
    
    # Generate context-aware, useful content
    if "slide" in prompt.lower() or "powerpoint" in prompt.lower():
        # Slide format - informative bullet points
        if is_coffee and "espresso" in title_lower:
            return f"""• Espresso is a concentrated coffee beverage brewed by forcing hot water through finely-ground coffee beans
• Originated in Italy in the early 20th century, named for the speed of preparation
• Characterized by rich, bold flavor and distinctive crema layer on top
• Typically served in small 1-2 ounce shots, stronger than regular coffee
• Made using high pressure (9 bars) and specific temperature (90-96°C)
• Base for many popular coffee drinks like cappuccino, latte, and Americano"""
        elif is_devotional and "greatness" in title_lower:
            return f"""• Divine attributes and cosmic significance
• Symbolism and spiritual meaning  
• Devotional practices and traditions
• Impact on spiritual seekers
• Timeless wisdom and teachings
• Universal reverence and worship"""
        elif is_devotional and "temple" in title_lower:
            return f"""• Historical and spiritual significance
• Architectural beauty and design
• Sacred rituals and ceremonies
• Devotee experiences and blessings
• Festivals and celebrations
• Pilgrimage importance"""
        elif is_technical and (is_healthcare_context or "health" in title_lower or "healthcare" in title_lower or "medical" in title_lower):
            # AI/Technology in Healthcare - specific content
            if "benefit" in title_lower:
                return f"""• Enhanced diagnostic accuracy through AI-powered medical imaging analysis
• Improved patient care with predictive analytics and early intervention systems
• Streamlined administrative processes reducing operational costs and wait times
• Personalized treatment plans based on comprehensive patient data analysis
• Accelerated drug discovery and medical research through AI algorithms
• Improved healthcare accessibility via telemedicine and remote monitoring"""
            elif "challenge" in title_lower or "problem" in title_lower or "issue" in title_lower:
                return f"""• Data privacy and security concerns with patient information
• Regulatory compliance and FDA approval requirements
• Integration challenges with existing healthcare systems
• High implementation costs and resource requirements
• Need for extensive training and change management
• Ethical considerations and algorithmic bias in AI decisions"""
            elif "application" in title_lower or "use" in title_lower or "current" in title_lower:
                return f"""• Medical imaging analysis for radiology and pathology
• Clinical decision support systems for diagnosis
• Electronic health records (EHR) management and analysis
• Drug discovery and pharmaceutical research
• Remote patient monitoring and telemedicine
• Administrative automation and workflow optimization"""
            elif "future" in title_lower or "scope" in title_lower or "trend" in title_lower:
                return f"""• Advanced AI diagnostics with higher accuracy rates
• Personalized medicine based on genetic and lifestyle data
• Predictive healthcare preventing diseases before onset
• AI-assisted surgery and robotic procedures
• Global healthcare accessibility through AI platforms
• Integration of AI with IoT and wearable devices"""
            else:
                return f"""• AI applications transforming healthcare delivery and patient outcomes
• Machine learning algorithms improving diagnostic precision and speed
• Data-driven insights enabling personalized medicine and treatment optimization
• Automation reducing administrative burden and improving efficiency
• Predictive analytics identifying health risks and enabling preventive care
• Integration challenges and solutions for healthcare AI implementation"""
        elif is_technical:
            return f"""• Core concepts and fundamental principles
• Technical specifications and requirements
• Implementation approaches and methodologies
• Best practices and industry standards
• Common challenges and solutions
• Future trends and developments"""
        elif is_business:
            return f"""• Market overview and current trends
• Key business strategies and approaches
• Competitive advantages and opportunities
• Implementation frameworks and processes
• Success metrics and KPIs
• Growth potential and future outlook"""
        elif is_science:
            return f"""• Scientific definition and fundamental principles
• Key research findings and discoveries
• Experimental methods and approaches
• Current understanding and theories
• Practical applications and implications
• Future research directions"""
        elif is_health:
            return f"""• Health definition and medical significance
• Key health benefits and considerations
• Important medical aspects and factors
• Prevention and treatment approaches
• Health implications and recommendations
• Summary of health-related information"""
        elif is_education:
            return f"""• Educational definition and learning objectives
• Key concepts and fundamental principles
• Teaching approaches and methodologies
• Learning outcomes and applications
• Educational benefits and importance
• Summary of educational content"""
        else:
            # Generate topic-specific content based on title words
            title_words = [w for w in title.split() if len(w) > 3]  # Get meaningful words
            if title_words:
                # Use the main topic word to generate more specific content
                main_topic = title_words[0] if title_words else title
                return f"""• Introduction to {main_topic} and its significance
• Key characteristics and defining features of {main_topic}
• Important aspects and practical applications
• Benefits, advantages, and value proposition
• Real-world examples and use cases
• Summary and key takeaways about {main_topic}"""
            else:
                return f"""• Definition and core concepts
• Key characteristics and features
• Important aspects and applications
• Benefits and advantages
• Practical examples and use cases
• Summary and key takeaways"""
    else:
        # Document section format - detailed, informative paragraphs
        if is_coffee and "espresso" in title_lower:
            return f"""Espresso is a concentrated coffee beverage that has become the foundation of modern coffee culture. Originating in Italy in the early 20th century, espresso gets its name from the Italian word meaning "pressed out" or "expressed," referring to the method of forcing hot water through finely-ground coffee beans under high pressure.

The preparation of espresso requires specific equipment and techniques. A typical espresso shot is made by forcing water at approximately 9 bars of pressure through 7-9 grams of finely-ground coffee beans at a temperature between 90-96°C (194-205°F). This process extracts the coffee's oils, flavors, and aromatic compounds in a concentrated form, typically producing 1-2 fluid ounces of liquid.

One of the distinguishing characteristics of espresso is the crema, a golden-brown foam layer that forms on top of a properly extracted shot. This crema is created by the emulsification of coffee oils and carbon dioxide released during the brewing process. The quality of the crema often indicates the quality of the espresso shot.

Espresso serves as the base for many popular coffee beverages, including cappuccino, latte, macchiato, and Americano. Its concentrated nature makes it ideal for mixing with milk, water, or other ingredients while maintaining a strong coffee flavor. The versatility and intensity of espresso have made it a cornerstone of coffee culture worldwide.

The flavor profile of espresso is typically described as bold, rich, and complex, with notes that can range from chocolatey and nutty to fruity and acidic, depending on the coffee beans used and the roasting process. Understanding espresso is essential for anyone interested in coffee, as it represents both a beverage in itself and the foundation for countless other coffee preparations."""
        elif is_devotional:
            return f"""{title} holds profound spiritual significance and represents deep devotional meaning. This topic encompasses important aspects of faith, tradition, and divine wisdom that have inspired countless devotees throughout history.

The key elements of {title} include spiritual teachings, devotional practices, and cultural traditions that form an integral part of religious understanding. These aspects work together to provide a comprehensive view of the subject matter and its importance in spiritual life.

Important aspects include the historical significance, symbolic meanings, devotional practices, and the impact on spiritual seekers. Understanding these elements provides valuable insights into the depth and richness of this spiritual topic.

This section covers the fundamental aspects of {title}, providing readers with a solid foundation for understanding its significance and importance in the broader context of spiritual and devotional practices."""
        elif is_technical and (is_healthcare_context or "health" in title_lower or "healthcare" in title_lower or "medical" in title_lower):
            # AI/Technology in Healthcare - detailed content
            if "benefit" in title_lower:
                return f"""{title} represents a transformative development in modern healthcare, leveraging artificial intelligence and advanced technologies to revolutionize medical practices and patient care. The integration of AI brings together cutting-edge technology with healthcare expertise to create innovative solutions that significantly improve outcomes, efficiency, and accessibility.

Enhanced diagnostic capabilities represent one of the most significant benefits. AI-powered systems can analyze medical images, including X-rays, MRIs, and CT scans, with remarkable accuracy, often detecting patterns and anomalies that might be missed by human analysis. Machine learning algorithms trained on vast datasets can identify early signs of diseases such as cancer, enabling earlier diagnosis and more effective treatment planning. This leads to improved patient outcomes and potentially saves lives through early intervention.

Predictive analytics enable healthcare providers to identify patients at risk for various conditions and intervene proactively. AI systems can analyze patient data including medical history, vital signs, lab results, and lifestyle factors to predict potential health complications before they become critical. This preventive approach reduces hospital readmissions, improves long-term patient health, and reduces overall healthcare costs.

Operational efficiency is dramatically improved through AI automation of administrative tasks such as appointment scheduling, billing processes, insurance claim processing, and documentation. Natural language processing enables automatic transcription of doctor-patient conversations into electronic health records, reducing the time healthcare professionals spend on paperwork and allowing them to focus more on direct patient care.

Personalized medicine is another major advantage, as AI can analyze individual patient data including genetics, medical history, treatment responses, and lifestyle factors to recommend customized treatment plans. This approach moves away from one-size-fits-all medicine toward treatments tailored to each patient's unique characteristics, improving effectiveness and reducing adverse effects.

The integration of AI in healthcare also accelerates medical research and drug discovery. AI algorithms can analyze vast amounts of scientific literature, clinical trial data, and molecular structures to identify potential drug candidates and treatment combinations much faster than traditional methods. This has the potential to bring new treatments to patients more quickly and at lower costs.

Telemedicine platforms enhanced with AI capabilities improve healthcare accessibility, especially for patients in remote areas or those with mobility limitations. AI-powered chatbots can provide initial triage, answer common health questions, and guide patients to appropriate care. Remote patient monitoring systems use AI to continuously track health metrics and alert healthcare providers to concerning changes, enabling timely intervention even when patients are at home.

These benefits collectively represent a significant advancement in healthcare delivery, improving both the quality of care and the efficiency of healthcare systems while making medical services more accessible to a broader population."""
            elif "challenge" in title_lower or "problem" in title_lower or "issue" in title_lower:
                return f"""{title} presents several important considerations that healthcare organizations must address when implementing artificial intelligence solutions. While AI offers tremendous potential, successful integration requires careful attention to various challenges and obstacles.

Data privacy and security represent primary concerns, as healthcare AI systems require access to sensitive patient information. Ensuring compliance with regulations such as HIPAA in the United States and GDPR in Europe is essential. Healthcare organizations must implement robust security measures, encryption protocols, and access controls to protect patient data from breaches and unauthorized access. The complexity of maintaining data security while enabling AI analysis creates ongoing challenges for IT departments.

Regulatory compliance and approval processes present significant hurdles. Medical AI applications often require FDA approval or similar regulatory clearance, which can be time-consuming and expensive. The regulatory landscape for AI in healthcare is still evolving, creating uncertainty for developers and healthcare providers. Ensuring that AI systems meet clinical standards and can be validated for safety and effectiveness requires extensive testing and documentation.

Integration with existing healthcare systems poses technical challenges. Many healthcare facilities use legacy electronic health record (EHR) systems that may not easily integrate with new AI technologies. Interoperability issues between different systems can prevent seamless data sharing and limit the effectiveness of AI solutions. Healthcare organizations must invest in infrastructure upgrades and middleware solutions to enable effective AI integration.

High implementation costs and resource requirements can be prohibitive for many healthcare organizations. AI systems require significant initial investment in hardware, software, training, and ongoing maintenance. Smaller healthcare facilities may struggle to afford these costs, potentially widening the gap between well-resourced and under-resourced healthcare providers. Additionally, the need for specialized IT staff and data scientists adds to operational expenses.

Training and change management represent critical challenges. Healthcare professionals must be trained to use AI tools effectively and understand their limitations. Resistance to change and concerns about AI replacing human judgment can create cultural barriers to adoption. Building trust in AI systems requires demonstrating their value, ensuring transparency in how decisions are made, and maintaining human oversight in critical decisions.

Ethical considerations and algorithmic bias are important concerns. AI systems trained on biased datasets may perpetuate or amplify existing healthcare disparities. Ensuring that AI algorithms are fair and equitable across different patient populations requires careful attention to dataset composition and algorithm design. The "black box" nature of some AI systems makes it difficult to understand how decisions are made, raising questions about accountability and transparency.

Addressing these challenges requires a comprehensive approach involving technology, policy, training, and cultural change. Despite these obstacles, the potential benefits of AI in healthcare make overcoming these challenges worthwhile for improving patient care and healthcare delivery."""
            elif "application" in title_lower or "use" in title_lower or "current" in title_lower:
                return f"""{title} encompasses a wide range of practical implementations where artificial intelligence is actively transforming healthcare delivery and improving patient outcomes. These applications represent real-world uses of AI technology that are currently being deployed in healthcare settings worldwide.

Medical imaging and diagnostic applications represent one of the most advanced areas of AI in healthcare. AI algorithms can analyze X-rays, CT scans, MRIs, mammograms, and other medical images with remarkable accuracy, often matching or exceeding the performance of experienced radiologists. These systems can detect tumors, fractures, abnormalities, and early signs of diseases such as cancer, enabling earlier diagnosis and treatment. Companies like Google Health and IBM Watson have developed AI systems that can identify diabetic retinopathy, skin cancer, and other conditions from medical images.

Clinical decision support systems use AI to assist healthcare providers in making diagnostic and treatment decisions. These systems analyze patient data including symptoms, medical history, lab results, and vital signs to suggest possible diagnoses and recommend treatment options. They can help reduce diagnostic errors, ensure adherence to clinical guidelines, and provide evidence-based recommendations. Epic Systems and Cerner have integrated AI-powered decision support into their electronic health record platforms.

Electronic health records (EHR) management benefits significantly from AI applications. Natural language processing enables automatic extraction of information from unstructured clinical notes, improving data entry efficiency and accuracy. AI can identify relevant information from patient records, flag important findings, and help organize information for easier access by healthcare providers. This reduces the time spent on documentation and improves the quality of patient records.

Drug discovery and pharmaceutical research have been revolutionized by AI applications. Machine learning algorithms can analyze vast databases of molecular structures, scientific literature, and clinical trial data to identify potential drug candidates. AI can predict how molecules will interact with biological targets, optimize drug formulations, and identify new uses for existing medications. Companies like Atomwise and BenevolentAI use AI to accelerate the drug discovery process, potentially reducing development time from years to months.

Remote patient monitoring and telemedicine applications leverage AI to enable continuous health tracking and virtual care delivery. Wearable devices and sensors can collect patient data including heart rate, blood pressure, glucose levels, and activity patterns. AI algorithms analyze this data to detect anomalies, predict health events, and alert healthcare providers to concerning changes. This enables proactive care management and reduces the need for frequent in-person visits, particularly valuable for patients with chronic conditions.

Administrative automation represents another important application area. AI-powered systems can automate appointment scheduling, insurance claim processing, billing, and prior authorization requests. Natural language processing enables chatbots and virtual assistants to handle patient inquiries, schedule appointments, and provide basic health information. This reduces administrative burden on healthcare staff and improves operational efficiency.

These current applications demonstrate the practical value of AI in healthcare, showing how technology can improve both clinical outcomes and operational efficiency while making healthcare more accessible and personalized."""
            elif "future" in title_lower or "scope" in title_lower or "trend" in title_lower:
                return f"""{title} represents an exciting frontier in healthcare technology, with tremendous potential for transforming medical practices and patient care in the coming years. The future of AI in healthcare promises even more advanced capabilities, broader adoption, and deeper integration into all aspects of healthcare delivery.

Advanced AI diagnostics will achieve even higher levels of accuracy and speed, potentially detecting diseases at earlier stages than currently possible. Future AI systems will integrate multiple data sources including medical images, genetic information, lab results, and patient history to provide comprehensive diagnostic insights. These systems may be able to identify diseases before symptoms appear, enabling truly preventive medicine. The development of explainable AI will make diagnostic decisions more transparent and trustworthy for healthcare providers.

Personalized medicine will reach new heights as AI systems become better at analyzing individual patient characteristics. Future applications will use comprehensive genetic profiling, microbiome analysis, lifestyle data, and real-time health monitoring to create highly customized treatment plans. AI will help identify which treatments will be most effective for specific patients, reducing trial-and-error approaches and improving treatment outcomes. This precision medicine approach will become standard practice rather than experimental.

Predictive healthcare will enable true prevention of diseases before they develop. AI systems will analyze patterns across large populations to identify risk factors and predict health outcomes with high accuracy. Healthcare providers will be able to intervene proactively, recommending lifestyle changes, preventive treatments, or monitoring strategies before conditions become serious. This shift from reactive to predictive healthcare will significantly improve population health and reduce healthcare costs.

AI-assisted surgery and robotic procedures will become more sophisticated and widely available. Surgical robots enhanced with AI will provide surgeons with real-time guidance, precision assistance, and enhanced visualization. AI systems will help plan complex surgeries, simulate procedures before they occur, and provide intraoperative support. These technologies will make advanced surgical procedures more accessible and reduce the risk of complications.

Global healthcare accessibility will be dramatically improved through AI-powered platforms that can deliver medical expertise to underserved areas. AI diagnostic systems running on mobile devices will enable healthcare delivery in remote locations without requiring extensive infrastructure. Telemedicine platforms enhanced with AI will provide specialist consultations to patients anywhere in the world. Language translation AI will break down barriers to healthcare access for diverse populations.

Integration of AI with Internet of Things (IoT) devices and wearable technology will create comprehensive health monitoring ecosystems. Smart devices will continuously collect health data, and AI systems will analyze this information in real-time to provide insights and alerts. This continuous monitoring will enable early detection of health issues and support proactive care management. The combination of AI and IoT will create a new paradigm of connected, data-driven healthcare.

The future scope of AI in healthcare also includes addressing current limitations and challenges. Research is ongoing to improve AI explainability, reduce algorithmic bias, ensure data privacy, and integrate AI more seamlessly into clinical workflows. As these challenges are addressed, AI adoption in healthcare will accelerate, leading to improved patient outcomes, reduced costs, and more accessible healthcare services worldwide."""
            else:
                return f"""{title} represents a fundamental concept in modern technology and computing, particularly in the healthcare domain. This topic encompasses core principles, implementation strategies, and practical applications that are essential for understanding how technology transforms healthcare delivery and patient outcomes.

The key aspects of {title} include technical specifications, architectural considerations, and implementation methodologies specific to healthcare environments. These elements work together to form a comprehensive understanding of how this technology functions within healthcare systems and how it can be effectively utilized to improve medical practices.

Important considerations include performance characteristics, scalability requirements, security implications for patient data, regulatory compliance, and integration challenges with existing healthcare infrastructure. Understanding these aspects is crucial for making informed decisions about adoption and implementation in healthcare settings.

This section provides a thorough examination of {title}, covering theoretical foundations, practical applications in healthcare, and best practices that will help readers develop a comprehensive understanding of this important technical topic in the medical field."""
        elif is_technical:
            return f"""{title} represents a fundamental concept in modern technology and computing. This topic encompasses core principles, implementation strategies, and practical applications that are essential for understanding contemporary technical systems.

The key aspects of {title} include technical specifications, architectural considerations, and implementation methodologies. These elements work together to form a comprehensive understanding of how this technology functions and how it can be effectively utilized in various contexts.

Important considerations include performance characteristics, scalability requirements, security implications, and integration challenges. Understanding these aspects is crucial for making informed decisions about adoption and implementation.

This section provides a thorough examination of {title}, covering theoretical foundations, practical applications, and best practices that will help readers develop a comprehensive understanding of this important technical topic."""
        elif is_business:
            return f"""{title} is a critical aspect of modern business strategy and operations. This topic encompasses key principles, strategic approaches, and practical applications that are essential for organizational success in today's competitive marketplace.

The fundamental elements of {title} include market analysis, strategic planning, implementation frameworks, and performance measurement. These components work together to create a comprehensive approach to business development and growth.

Key considerations include market opportunities, competitive positioning, resource allocation, and risk management. Understanding these factors is essential for making informed business decisions and achieving sustainable competitive advantages.

This section provides an in-depth exploration of {title}, covering strategic concepts, practical applications, and real-world examples that will help readers understand how to effectively implement and manage this important business function."""
        elif is_science:
            return f"""{title} represents an important scientific concept that plays a significant role in our understanding of the natural world. This topic encompasses fundamental principles, research findings, and practical applications that are essential for scientific knowledge.

The scientific aspects of {title} include theoretical foundations, experimental evidence, and empirical observations. These elements work together to form a comprehensive understanding of how this concept functions within scientific frameworks and contributes to broader scientific knowledge.

Key scientific considerations include the definition and scope of the concept, its relationship to other scientific principles, current research and understanding, and practical applications in scientific contexts. Understanding these aspects is crucial for a thorough grasp of this scientific topic.

This section provides a detailed scientific exploration of {title}, covering theoretical foundations, research findings, and practical applications that will help readers develop a comprehensive understanding of this important scientific concept."""
        elif is_health:
            return f"""{title} is an important health-related topic that has significant implications for well-being and medical understanding. This subject encompasses key health concepts, medical information, and practical health considerations that are essential for maintaining good health.

The health aspects of {title} include medical definitions, health benefits or concerns, preventive measures, and treatment approaches where applicable. These elements work together to provide a comprehensive view of how this topic relates to health and wellness.

Important health considerations include understanding the health implications, recognizing key health factors, identifying preventive strategies, and knowing when to seek medical advice. Each of these aspects contributes to a thorough understanding of the health-related dimensions of this topic.

This section provides a detailed health-focused exploration of {title}, covering essential health information, medical considerations, and practical health guidance that will help readers understand the health-related aspects of this important topic."""
        elif is_education:
            return f"""{title} is a fundamental educational topic that plays an important role in learning and knowledge acquisition. This subject encompasses key educational concepts, learning objectives, and teaching approaches that are essential for effective education.

The educational aspects of {title} include learning objectives, core concepts, teaching methodologies, and assessment strategies. These elements work together to form a comprehensive educational framework that supports effective learning and knowledge transfer.

Key educational considerations include understanding the learning goals, identifying core concepts and principles, exploring effective teaching methods, and recognizing practical applications in educational contexts. Understanding these aspects is crucial for both educators and learners.

This section provides a detailed educational exploration of {title}, covering learning objectives, core concepts, teaching approaches, and practical applications that will help readers develop a comprehensive understanding of this important educational topic."""
        else:
            # Generate more specific content based on the actual title
            title_words = [w for w in title.split() if len(w) > 3]  # Get meaningful words
            if title_words:
                main_topic = title_words[0] if title_words else title
                return f"""{title} is a significant topic that encompasses multiple important aspects and dimensions. Understanding {main_topic} requires examining its core concepts, key characteristics, and practical applications in various contexts.

The fundamental elements of {title} include essential principles, defining characteristics, and relevant applications that contribute to a comprehensive understanding. These components work together to form a complete picture of {main_topic} and its significance.

Key aspects to consider include the definition and scope of {main_topic}, its key characteristics and features, important applications and use cases, and the benefits or value it provides. Each of these dimensions contributes to a thorough understanding of the subject matter.

This section provides a detailed exploration of {title}, covering essential information about {main_topic}, important concepts, practical applications, and key insights that will help readers develop a comprehensive understanding of this important topic."""
            else:
                return f"""{title} is a significant topic that encompasses multiple important aspects and dimensions. Understanding this subject requires examining its core concepts, historical context, and practical applications.

The fundamental elements of {title} include key principles, important characteristics, and relevant applications. These components work together to form a comprehensive understanding of the topic and its significance in various contexts.

Key aspects to consider include the definition and scope of the topic, its historical development, current applications and relevance, and future implications. Each of these dimensions contributes to a thorough understanding of the subject matter.

This section provides a detailed exploration of {title}, covering essential information, important concepts, and practical insights that will help readers develop a comprehensive understanding of this important topic."""


def _refine_content_fallback(
    original_content: str,
    refinement_prompt: str,
    content_type: str = "section"
) -> str:
    """Intelligent fallback refinement that actually modifies content based on common requests"""
    refinement_lower = refinement_prompt.lower()
    
    # Extract title from original content if possible
    title = ""
    lines = original_content.split('\n')
    if lines:
        first_line = lines[0].strip()
        # If first line looks like a title (short, no period, etc.)
        if len(first_line) < 100 and not first_line.endswith('.'):
            title = first_line
    
    # Remove any instruction text that might have leaked into original content
    cleaned_original = original_content
    if "Please provide the refined content" in cleaned_original:
        parts = cleaned_original.split("Please provide the refined content")
        cleaned_original = parts[0].strip()
    
    # Common refinement patterns
    if any(word in refinement_lower for word in ["make longer", "expand", "add more", "more detail", "more information"]):
        # Expand the content
        if content_type == "slide":
            if "•" in cleaned_original or "-" in cleaned_original:
                return cleaned_original + "\n• Additional relevant information and insights\n• Further details and considerations\n• Important aspects to consider"
            else:
                return cleaned_original + "\n\n• Additional key points\n• Further considerations\n• Important details"
        else:
            return cleaned_original + "\n\nThis topic encompasses additional important aspects that warrant further exploration. Understanding these elements provides deeper insights into the subject matter and its broader implications."
    
    elif any(word in refinement_lower for word in ["make shorter", "condense", "summarize", "brief", "concise"]):
        # Condense the content
        if content_type == "slide":
            lines = cleaned_original.split('\n')
            bullet_lines = [line for line in lines if line.strip().startswith('•') or line.strip().startswith('-')]
            if bullet_lines:
                return '\n'.join(bullet_lines[:4])
            else:
                sentences = cleaned_original.split('.')
                return '. '.join(sentences[:2]) + '.'
        else:
            paragraphs = cleaned_original.split('\n\n')
            return paragraphs[0] if paragraphs else cleaned_original[:200] + "..."
    
    elif any(word in refinement_lower for word in ["simpler", "simple", "easy", "understand", "explain"]):
        # Simplify language
        simplified = cleaned_original.replace("encompasses", "includes")
        simplified = simplified.replace("comprehensive", "complete")
        simplified = simplified.replace("fundamental", "basic")
        return simplified
    
    elif any(word in refinement_lower for word in ["improve", "better", "enhance", "quality"]):
        # Improve the content
        if content_type == "slide":
            if "•" not in cleaned_original:
                sentences = cleaned_original.split('.')
                bullet_points = [f"• {s.strip()}" for s in sentences if s.strip()][:6]
                return '\n'.join(bullet_points)
            else:
                return cleaned_original + "\n• Enhanced implementation strategies\n• Best practices and recommendations"
        else:
            return cleaned_original + "\n\nTo further enhance understanding, it is important to consider practical applications and real-world examples that demonstrate the relevance of these concepts."
    
    # If refinement prompt is asking about a specific topic, try to incorporate it
    if any(word in refinement_lower for word in ["about", "explain", "what is", "define"]):
        # User wants explanation of the title/topic
        if title:
            if content_type == "slide":
                return f"""• {title} refers to important concepts and applications in this field
• Key characteristics and defining features
• Practical applications and real-world uses
• Benefits and advantages
• Current trends and future developments"""
            else:
                return f"""{title} represents an important concept that encompasses multiple key aspects and practical applications. Understanding this topic requires examining its fundamental principles, key characteristics, and real-world relevance.

The core elements of {title} include essential concepts, defining features, and practical applications that demonstrate its significance. These components work together to provide a comprehensive understanding of the subject matter and its importance in various contexts.

Key considerations include the definition and scope of {title}, its key characteristics and features, important applications and use cases, and the benefits or value it provides. Each of these dimensions contributes to a thorough understanding of the topic."""
    
    # Default: return cleaned original content (remove any instruction text)
    return cleaned_original


def generate_section_content(
    section_title: str,
    project_context: Optional[str] = None,
    previous_sections: Optional[List[str]] = None
) -> str:
    """Generate content for a Word document section"""
    context_parts = []
    
    if project_context:
        context_parts.append(f"Project context: {project_context}")
    
    if previous_sections:
        context_parts.append(f"Previous sections: {', '.join(previous_sections)}")
    
    context = "\n".join(context_parts) if context_parts else None
    
    prompt = f"""Generate comprehensive content for a document section titled "{section_title}".

Requirements:
- Write detailed, professional content appropriate for this section
- Use proper formatting and structure
- Include relevant information and examples where appropriate
- Maintain consistency with the overall document theme
- Aim for 300-500 words

Section Title: {section_title}"""
    
    return _generate_with_retry(prompt, context)


def generate_slide_content(
    slide_title: str,
    project_context: Optional[str] = None,
    previous_slides: Optional[List[str]] = None
) -> str:
    """Generate content for a PowerPoint slide"""
    context_parts = []
    
    if project_context:
        context_parts.append(f"Presentation context: {project_context}")
    
    if previous_slides:
        context_parts.append(f"Previous slides: {', '.join(previous_slides)}")
    
    context = "\n".join(context_parts) if context_parts else None
    
    prompt = f"""Generate content for a PowerPoint slide titled "{slide_title}".

Requirements:
- Create concise, bullet-point style content suitable for a presentation slide
- Include key points and main ideas
- Use clear, impactful language
- Keep content brief (suitable for a slide format)
- Maintain consistency with the overall presentation theme

Slide Title: {slide_title}"""
    
    return _generate_with_retry(prompt, context)


def refine_content(
    original_content: str,
    refinement_prompt: str,
    content_type: str = "section"  # "section" or "slide"
) -> str:
    """Refine existing content based on user prompt"""
    # If using mock/fallback mode, use intelligent fallback refinement
    if settings.MOCK_LLM:
        return _refine_content_fallback(original_content, refinement_prompt, content_type)
    
    prompt = f"""Refine the following {content_type} content based on the user's request.

Original Content:
{original_content}

User's Refinement Request:
{refinement_prompt}

Please provide the refined content that addresses the user's request while maintaining the overall quality and style of the original content."""
    
    return _generate_with_retry(prompt)
