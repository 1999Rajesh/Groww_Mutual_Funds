'use client';

import { Provider } from 'react-redux';
import { store } from '../lib/store';
import ChatInterface from '../components/ChatInterface';

export default function Home() {
  return (
    <Provider store={store}>
      <main className="min-h-screen">
        <ChatInterface />
      </main>
    </Provider>
  );
}
