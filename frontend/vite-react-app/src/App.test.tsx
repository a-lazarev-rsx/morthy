import { render, screen } from '@testing-library/react';
import App from './App';
import { describe, it, expect } from 'vitest';

describe('App Component', () => {
  it('renders the main page with buttons and card', () => {
    render(<App />);
    // Check for buttons
    expect(screen.getByRole('button', { name: /Soft Yellow Button/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Soft Orange Button/i })).toBeInTheDocument();

    // Check for card title
    expect(screen.getByText('Themed Card Title')).toBeInTheDocument();
  });
});
