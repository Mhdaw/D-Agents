import { cookies } from 'next/headers';

import { ClientWrapper } from '@/components/ClientWrapper';

export const experimental_ppr = true;

export default async function Layout({
  children,
}: {
  children: React.ReactNode;
}) {



  return (
    <ClientWrapper 
      session={undefined}
      isCollapsed={false}
    >
      {children}
    </ClientWrapper>
  );
}