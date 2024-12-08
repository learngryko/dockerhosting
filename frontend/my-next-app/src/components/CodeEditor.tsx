// components/CodeEditor.tsx

"use client";

import React from 'react';
import dynamic from 'next/dynamic';
import { loader } from '@monaco-editor/react';

// Dynamically import the Monaco Editor to prevent SSR issues
const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

// Optional: Configure Monaco Editor to load additional languages or themes
loader.config({
  paths: {
    vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.34.1/min/vs',
  },
});

interface CodeEditorProps {
  language: string;
  value: string;
  onChange: (value: string | undefined) => void;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ language, value, onChange }) => {
  return (
    <MonacoEditor
      height="100%"
      language={language}
      value={value}
      theme="vs-dark" // You can switch to 'light' or other themes
      onChange={onChange}
      options={{
        selectOnLineNumbers: true,
        automaticLayout: true,
        minimap: { enabled: false },
        scrollbar: {
          verticalScrollbarSize: 8,
          horizontalScrollbarSize: 8,
        },
      }}
    />
  );
};

export default CodeEditor;
