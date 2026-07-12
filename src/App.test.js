import { render, screen } from '@testing-library/react';
import App from './App';

jest.mock('react-leaflet', () => ({
  MapContainer: ({ children }) => <div>{children}</div>,
  GeoJSON: ({ children }) => <div>{children}</div>,
  Popup: ({ children }) => <div>{children}</div>
}));

test('shows the alert summary and legend', () => {
  render(<App />);

  expect(screen.getByRole('heading', { name: 'Мапа повітряних тривог' })).toBeInTheDocument();
  expect(screen.getByText(/регіонів зараз у тривозі/)).toBeInTheDocument();
  expect(screen.getByLabelText('Умовні позначення')).toBeInTheDocument();
});
