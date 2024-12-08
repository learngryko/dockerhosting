// utils/buildFileTree.ts

export interface FileItem {
    file_path: string;
    extension: string;
  }
  
  export interface TreeNode {
    name: string;
    type: 'file' | 'folder';
    children?: TreeNode[];
  }
  
  export const buildFileTree = (files: FileItem[]): TreeNode[] => {
    const root: TreeNode = { name: 'root', type: 'folder', children: [] };
  
    files.forEach((file) => {
      const parts = file.file_path.split('/');
      let currentNode = root;
  
      parts.forEach((part, index) => {
        const isFile = index === parts.length - 1;
        let existingNode = currentNode.children?.find((child) => child.name === part);
  
        if (!existingNode) {
          existingNode = {
            name: part,
            type: isFile ? 'file' : 'folder',
            children: isFile ? undefined : [],
          };
          currentNode.children?.push(existingNode);
        }
  
        if (!isFile && existingNode.children) {
          currentNode = existingNode;
        }
      });
    });
  
    // Return the children of the root node, effectively excluding 'root'
    return root.children || [];
  };
  