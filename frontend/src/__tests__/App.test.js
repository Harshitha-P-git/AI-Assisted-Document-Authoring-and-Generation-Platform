import { render } from '@testing-library/react';
import App from '../App';

test('renders app', () => {
  render(<App />);
  // Basic smoke test
  expect(document.body).toBeTruthy();
});
