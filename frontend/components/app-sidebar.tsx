'use client';

import type { User } from 'next-auth';
import { MessageSquare, Mic, Volume2, Gamepad, ChartBarStacked, RectangleVerticalIcon, ChartBarIncreasingIcon } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';

import { PlusIcon } from '@/components/icons';
// import { SidebarHistory } from '@/components/sidebar-history';
import { SidebarUserNav } from '@/components/sidebar-user-nav';
import { Button } from '@/components/ui/button';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  useSidebar,
} from '@/components/ui/sidebar';
import { BetterTooltip } from '@/components/ui/tooltip';

interface AppSidebarProps {
  user?: User;
  currentMode?: string;
  setCurrentMode?: (mode: string) => void;
}

export function AppSidebar({ user, currentMode = 'chat', setCurrentMode }: AppSidebarProps) {
  const { setOpenMobile } = useSidebar();
  const [activeHistory, setActiveHistory] = useState<string[]>([]);
  const [localMode, setLocalMode] = useState(currentMode);

  // Use either provided setCurrentMode or local state
  const handleModeChange = (mode: string) => {
    if (setCurrentMode) {
      setCurrentMode(mode);
    } else {
      setLocalMode(mode);
    }
    setOpenMobile(false);
  };

  // Use either provided currentMode or local state
  const activeMode = currentMode || localMode;

  const modes = [
    { id: 'Trade', icon: ChartBarIncreasingIcon, label: 'Ai Trading', color: 'text-blue-500' },
    { id: 'Portfolio Manager', icon: Mic, label: 'Portfolio Manager', color: 'text-green-500' },
    { id: 'Bridge', icon: RectangleVerticalIcon, label: 'Bridge', color: 'text-purple-500' },
    { id: 'Stake', icon: ChartBarStacked, label: 'Stake', color: 'text-orange-500' },
    { id: 'Compete', icon: Gamepad, label: 'Compete and Earn', color: 'text-orange-500' },
  ];

  const handleNewSession = () => {
    setOpenMobile(false);
    const newSessionId = `${activeMode}-${Date.now()}`;
    setActiveHistory([newSessionId, ...activeHistory]);
  };

  return (
    <Sidebar className="group-data-[side=left]:border-r-0">
      <SidebarHeader className="pb-4">
        <SidebarMenu>
          <div className="flex flex-col gap-6 pl-4">
            <Link
              href="/"
              onClick={() => setOpenMobile(false)}
              className="mt-6 mb-2"
            >
              <span className="text-3xl font-bold hover:bg-muted rounded-md cursor-pointer px-2 py-1">
                1trillion
              </span>
            </Link>
            
            <div className="flex flex-col gap-2">
              {modes.map(({ id, icon: Icon, label, color }) => (
                <Button
                  key={id}
                  variant="ghost"
                  className={`justify-start gap-2 ${
                    activeMode === id 
                      ? 'bg-muted font-medium' 
                      : 'hover:bg-muted/50'
                  }`}
                  onClick={() => handleModeChange(id)}
                >
                  <Icon className={`h-5 w-5 ${activeMode === id ? color : ''}`} />
                  {label}
                </Button>
              ))}
            </div>

            <BetterTooltip content={`New ${activeMode.charAt(0).toUpperCase() + activeMode.slice(1)}`}>
              <Button
                className="mr-10 ml-2 rounded-3xl border border-b-4 border-gray-600 hover:bg-muted/80 transition-colors"
                variant="outline"
                type="button"
                onClick={handleNewSession}
              >
                <PlusIcon  />
                <span>New {activeMode.charAt(0).toUpperCase() + activeMode.slice(1)}</span>
              </Button>
            </BetterTooltip>
          </div>
        </SidebarMenu>
      </SidebarHeader>
      
      <SidebarContent className="px-4">
        <SidebarGroup>
          <SidebarGroupContent className="px-2">
            <div className="text-sm font-medium text-muted-foreground mb-2">
              Recent {activeMode.charAt(0).toUpperCase() + activeMode.slice(1)} History
            </div>
            {/* Only pass the props that SidebarHistory accepts */}
            {/* <SidebarHistory user={user} /> */}
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      
      <SidebarFooter className="border-t mt-auto">
        {user && (
          <SidebarGroup>
            <SidebarGroupContent className="px-2">
              <SidebarUserNav user={user} />
            </SidebarGroupContent>
          </SidebarGroup>
        )}
      </SidebarFooter>
    </Sidebar>
  );
}