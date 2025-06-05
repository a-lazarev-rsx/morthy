import { render, screen } from '@testing-library/react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from './card';
import { describe, it, expect } from 'vitest';

describe('Card Component and Sub-components', () => {
  it('renders a Card with all its parts and content', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Test Card Title</CardTitle>
          <CardDescription>Test Card Description</CardDescription>
        </CardHeader>
        <CardContent>
          <p>Test card content paragraph.</p>
        </CardContent>
        <CardFooter>
          <p>Test card footer content.</p>
        </CardFooter>
      </Card>
    );

    // Check for Card title, description, content, and footer
    expect(screen.getByText('Test Card Title')).toBeInTheDocument();
    expect(screen.getByText('Test Card Description')).toBeInTheDocument();
    expect(screen.getByText('Test card content paragraph.')).toBeInTheDocument();
    expect(screen.getByText('Test card footer content.')).toBeInTheDocument();

    // Check for base classes to ensure components are rendering with shadcn/ui styles
    const cardElement = screen.getByText('Test Card Title').closest('div[class*="rounded-lg"]');
    expect(cardElement).toHaveClass('bg-card');
    expect(cardElement).toHaveClass('text-card-foreground');
    expect(cardElement).toHaveClass('border'); // Ensure border class is present

    const cardHeaderElement = screen.getByText('Test Card Title').parentElement;
    expect(cardHeaderElement).toHaveClass('flex');
    expect(cardHeaderElement).toHaveClass('flex-col');
    expect(cardHeaderElement).toHaveClass('space-y-1.5');
    expect(cardHeaderElement).toHaveClass('p-6');

    const cardTitleElement = screen.getByText('Test Card Title');
    expect(cardTitleElement.tagName).toBe('H3');
    expect(cardTitleElement).toHaveClass('text-2xl');
    expect(cardTitleElement).toHaveClass('font-semibold');
    expect(cardTitleElement).toHaveClass('leading-none');
    expect(cardTitleElement).toHaveClass('tracking-tight');

    const cardDescriptionElement = screen.getByText('Test Card Description');
    expect(cardDescriptionElement.tagName).toBe('P');
    expect(cardDescriptionElement).toHaveClass('text-sm');
    expect(cardDescriptionElement).toHaveClass('text-muted-foreground');

    const cardContentElement = screen.getByText('Test card content paragraph.').parentElement;
    expect(cardContentElement).toHaveClass('p-6');
    expect(cardContentElement).toHaveClass('pt-0');

    const cardFooterElement = screen.getByText('Test card footer content.').parentElement;
    expect(cardFooterElement).toHaveClass('flex');
    expect(cardFooterElement).toHaveClass('items-center');
    expect(cardFooterElement).toHaveClass('p-6');
    expect(cardFooterElement).toHaveClass('pt-0');
  });
});
