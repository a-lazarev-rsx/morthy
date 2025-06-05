import { render } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import './main'; // Import to execute the file

describe('main.tsx', () => {
  it('renders the App component into the root element', () => {
    const rootElement = document.getElementById('root');
    // We expect that render is called from main.tsx
    // Vitest doesn't directly support spying on ReactDOM.createRoot().render easily
    // without more complex mocking. Instead, we will check if the #root element
    // has content after main.tsx runs (which it should if React 18+ is rendering correctly)
    // A more robust test would involve mocking React's internals or using a different setup.
    // For now, we check if the root element is populated.
    expect(rootElement).not.toBeNull();
    if (rootElement) { // Type guard for TypeScript
      expect(rootElement.innerHTML).not.toBe('');
    }
  });
});
