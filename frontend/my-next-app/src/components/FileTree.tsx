// components/FileTree.tsx

"use client";

import { useState } from 'react';
import { ChevronRightIcon, ChevronDownIcon, DocumentIcon, FolderIcon, FolderOpenIcon } from '@heroicons/react/24/solid';

interface TreeNode {
  name: string;
  type: 'file' | 'folder';
  children?: TreeNode[];
}

interface FileTreeProps {
  node: TreeNode;
  onFileSelect: (filePath: string) => void;
  currentPath: string;
}

const FileTree: React.FC<FileTreeProps> = ({ node, onFileSelect, currentPath }) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [isSelected, setIsSelected] = useState<boolean>(false);

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  const handleFileClick = () => {
    const fullPath = currentPath ? `${currentPath}/${node.name}` : node.name;
    onFileSelect(fullPath);
    setIsSelected(true);
  };

  return (
    <div className="ml-4">
      {node.type === 'folder' ? (
        <div>
          <div
            className="flex items-center cursor-pointer hover:bg-gray-100 p-1 rounded"
            onClick={handleToggle}
            role="button"
            tabIndex={0}
            onKeyPress={(e) => {
              if (e.key === 'Enter') handleToggle();
            }}
            aria-label={`Toggle folder ${node.name}`}
          >
            {isOpen ? (
              <FolderOpenIcon className="h-4 w-4 mr-1 text-yellow-500" />
            ) : (
              <FolderIcon className="h-4 w-4 mr-1 text-yellow-500" />
            )}
            <span className="font-semibold">{node.name}</span>
            {isOpen ? (
              <ChevronDownIcon className="h-4 w-4 ml-auto text-gray-500" />
            ) : (
              <ChevronRightIcon className="h-4 w-4 ml-auto text-gray-500" />
            )}
          </div>
          {isOpen && node.children && (
            <div>
              {node.children.map((child) => (
                <FileTree
                  key={child.name}
                  node={child}
                  onFileSelect={onFileSelect}
                  currentPath={currentPath ? `${currentPath}/${node.name}` : node.name}
                />
              ))}
            </div>
          )}
        </div>
      ) : (
        <div
          className={`flex items-center cursor-pointer hover:bg-gray-100 p-1 rounded ${isSelected ? 'bg-blue-100' : ''
            }`}
          onClick={handleFileClick}
          role="button"
          tabIndex={0}
          onKeyPress={(e) => {
            if (e.key === 'Enter') handleFileClick();
          }}
          aria-label={`Select file ${node.name}`}
        >
          <DocumentIcon className="h-4 w-4 mr-1 text-gray-500" />
          <span className="ml-1">{node.name}</span>
        </div>
      )}
    </div>
  );
};

export default FileTree;
