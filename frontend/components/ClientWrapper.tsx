'use client'
import { useState } from 'react';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';
import { AppSidebar } from '@/components/app-sidebar';

export function ClientWrapper({ 
  session, 
  isCollapsed, 
  children 
}: { 
  session: any;
  isCollapsed: boolean;
  children: React.ReactNode;
}) {
  const [currentMode, setCurrentMode] = useState('chat');

  return (
    <SidebarProvider defaultOpen={!isCollapsed}>
      <AppSidebar 
        user={session?.user} 
        currentMode={currentMode}
        setCurrentMode={setCurrentMode}
      />
      <SidebarInset>{children}</SidebarInset>
    </SidebarProvider>
  );
}