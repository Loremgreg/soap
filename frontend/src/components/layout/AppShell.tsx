import { Header } from './Header';
import { BottomNav } from './BottomNav';

/**
 * Props for AppShell component.
 */
interface AppShellProps {
  children: React.ReactNode;
}

/**
 * Main application shell layout with header and bottom navigation.
 *
 * Features:
 * - Sticky header with app title and QuotaWidget
 * - Bottom navigation with Home, History, Settings
 * - Centered content area with max-width for larger screens
 * - Mobile-first design that scales gracefully to tablet/desktop
 *
 * @param props - Component props
 * @param props.children - Page content to render
 * @returns Application shell component
 */
export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      {children}
      <BottomNav />
    </div>
  );
}
