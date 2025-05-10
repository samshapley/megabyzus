'use client';

import { useState } from 'react';
import Image from 'next/image';

// Types for display items
interface ImageItem {
  type: 'image';
  src: string;
  alt: string;
  width: number;
  height: number;
}

interface TextItem {
  type: 'text';
  content: string;
}

interface CodeItem {
  type: 'code';
  language: string;
  content: string;
}

interface DataItem {
  type: 'data';
  data: any;
  format: 'json' | 'table';
}

type DisplayItem = ImageItem | TextItem | CodeItem | DataItem;

interface DisplayPanelProps {
  items: DisplayItem[];
}

export default function DisplayPanel({ items = [] }: DisplayPanelProps) {
  // In a real implementation, we might have more state management here
  // for handling different types of display items

  return (
    <div className="h-full flex flex-col">
      <div className="py-3 px-4 border-b border-white/10">
        <h2 className="font-semibold">Artifacts</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        {items.length === 0 ? (
          // Empty state
          <div className="h-full flex flex-col items-center justify-center text-center p-6">
            <div className="w-16 h-16 mb-4 rounded-full border border-white/20 flex items-center justify-center">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                width="24" 
                height="24" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
                className="text-white/60"
              >
                <rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect>
                <circle cx="9" cy="9" r="2"></circle>
                <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"></path>
              </svg>
            </div>
            <h3 className="text-xl font-medium mb-2">No artifacts yet</h3>
            <p className="text-secondary-text">
              Images, data, and other artifacts from your conversation will appear here.
            </p>
          </div>
        ) : (
          // Display items
          <div className="space-y-4">
            {items.map((item, index) => (
              <div 
                key={index} 
                className="bg-secondary-background rounded-lg overflow-hidden animate-fade-in"
              >
                {renderItem(item, index)}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Helper function to render different types of display items
function renderItem(item: DisplayItem, index: number) {
  switch (item.type) {
    case 'image':
      return (
        <div className="relative">
          <Image
            src={item.src}
            alt={item.alt}
            width={item.width}
            height={item.height}
            className="w-full h-auto"
          />
        </div>
      );
    
    case 'text':
      return (
        <div className="p-4">
          <p>{item.content}</p>
        </div>
      );
    
    case 'code':
      return (
        <div className="p-4">
          <pre className="overflow-x-auto">
            <code>{item.content}</code>
          </pre>
        </div>
      );
    
    case 'data':
      if (item.format === 'json') {
        return (
          <div className="p-4">
            <pre className="overflow-x-auto">
              <code>{JSON.stringify(item.data, null, 2)}</code>
            </pre>
          </div>
        );
      }
      
      if (item.format === 'table') {
        // Very basic table rendering - in a real application, we would use a proper table component
        return (
          <div className="p-4 overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr>
                  {Object.keys(item.data[0] || {}).map((key) => (
                    <th key={key} className="border border-white/20 p-2 text-left">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {item.data.map((row: any, rowIndex: number) => (
                  <tr key={rowIndex}>
                    {Object.values(row).map((cell: any, cellIndex: number) => (
                      <td key={cellIndex} className="border border-white/20 p-2">
                        {typeof cell === 'object' ? JSON.stringify(cell) : String(cell)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }
      
      return (
        <div className="p-4">
          <p>Unsupported data format</p>
        </div>
      );
    
    default:
      return (
        <div className="p-4">
          <p>Unsupported item type</p>
        </div>
      );
  }
}