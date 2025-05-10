'use client';

import { useState, useEffect } from 'react';

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  // Add a small animation effect when the component mounts
  const [isLoaded, setIsLoaded] = useState(false);
  
  useEffect(() => {
    setIsLoaded(true);
  }, []);
  
  return (
    <div 
      className={`h-screen flex flex-col overflow-hidden ${
        isLoaded ? 'opacity-100' : 'opacity-0'
      } transition-opacity duration-500`}
    >
      {/* Header removed as requested */}
      
      <main className="flex-1 flex flex-col overflow-hidden">
        {children}
      </main>
    </div>
  );
}
