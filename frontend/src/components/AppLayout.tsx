import { AppSidebar } from '@/components/AppSidebar';

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="min-h-screen flex w-full gradient-dark">
      <AppSidebar />
      <main className="flex-1 overflow-auto">
        <div className="gradient-glow min-h-screen">
          <div className="container py-8 px-6 max-w-7xl">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
