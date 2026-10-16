import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the EduNúñez home page', () => {
  render(<App />);
  expect(screen.getByRole('heading', { name: /Plataforma Educativa/ })).toBeInTheDocument();
});
