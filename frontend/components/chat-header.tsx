'use client';

import { useRouter } from 'next/navigation';
import { useWindowSize } from 'usehooks-ts';
import { Grid, Settings } from 'lucide-react';

import { SidebarToggle } from '@/components/sidebar-toggle';
import { Button } from '@/components/ui/button';
import { BetterTooltip } from '@/components/ui/tooltip';
import { useSidebar } from './ui/sidebar';

export function ChatHeader() {


  return (
    <div>
      <div className="sticky top-0 bg-background">
        <div className="flex items-center px-2 md:px-2 py-1.5 gap-2">
          <SidebarToggle />
          <span className="font-medium">Chatbot</span>
          <div className="flex gap-2 ml-auto">
            <BetterTooltip content="Grid View">
              <Button variant="ghost" size="icon" className="h-9 w-9">
                <Grid className="h-5 w-5" />
              </Button>
            </BetterTooltip>
            <BetterTooltip content="Settings">
              <Button variant="ghost" size="icon" className="h-9 w-9">
                <Settings className="h-5 w-5" />
              </Button>
            </BetterTooltip>
          </div>
        </div>
        
       
      </div>
    </div>
  );
}