import { render, screen } from '@testing-library/react';
import { Button } from './button';
import { describe, it, expect } from 'vitest';

describe('Button Component', () => {
  it('renders correctly with text', () => {
    render(<Button>Click Me</Button>);
    const buttonElement = screen.getByRole('button', { name: /Click Me/i });
    expect(buttonElement).toBeInTheDocument();
  });

  it('applies custom background color classes', () => {
    render(<Button className="bg-softYellow text-softYellow-foreground">Soft Yellow Button</Button>);
    const buttonElement = screen.getByRole('button', { name: /Soft Yellow Button/i });
    expect(buttonElement).toHaveClass('bg-softYellow');
    expect(buttonElement).toHaveClass('text-softYellow-foreground');
  });

  it('applies default variant classes if no variant is specified', () => {
    render(<Button>Default Button</Button>);
    const buttonElement = screen.getByRole('button', { name: /Default Button/i });
    // Check for default variant classes (e.g., bg-primary, text-primary-foreground)
    // These are defined in the buttonVariants object in button.jsx
    expect(buttonElement).toHaveClass('bg-primary');
    expect(buttonElement).toHaveClass('text-primary-foreground');
  });

  it('applies specified variant classes', () => {
    render(<Button variant="destructive">Destructive Button</Button>);
    const buttonElement = screen.getByRole('button', { name: /Destructive Button/i });
    expect(buttonElement).toHaveClass('bg-destructive');
    expect(buttonElement).toHaveClass('text-destructive-foreground');
  });

  it('renders as a child component when asChild prop is true', () => {
    render(
      <Button asChild>
        <a href="/">Link Button</a>
      </Button>
    );
    // Check for the anchor tag, not button role
    const linkElement = screen.getByRole('link', { name: /Link Button/i });
    expect(linkElement).toBeInTheDocument();
    // Check that it still has button-like styling from buttonVariants
    expect(linkElement).toHaveClass('bg-primary'); // Default variant
    expect(linkElement).toHaveClass('text-primary-foreground');
  });
});
