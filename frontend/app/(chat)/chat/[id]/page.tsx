
import { cookies } from 'next/headers';
import { notFound } from 'next/navigation';


import { Chat as PreviewChat } from '@/components/chat';

export default async function Page(props: { params: Promise<{ id: string }> }) {

  return (
    <PreviewChat
    />
  );
}
