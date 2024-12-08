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

export const buildFileTree = (files: FileItem[], searchTerm: string = ''): TreeNode[] => {
  const tree: TreeNode[] = [];

  files.forEach(file => {
    if (searchTerm && !file.file_path.toLowerCase().includes(searchTerm.toLowerCase())) {
      return; // Skip files that don't match the search term
    }

    const parts = file.file_path.split('/');
    let currentLevel = tree;

    parts.forEach((part, index) => {
      const existingNode = currentLevel.find(node => node.name === part);

      if (existingNode) {
        if (existingNode.type === 'folder') {
          currentLevel = existingNode.children!;
        }
      } else {
        const newNode: TreeNode = {
          name: part,
          type: index === parts.length - 1 ? 'file' : 'folder',
          children: index === parts.length - 1 ? undefined : [],
        };
        currentLevel.push(newNode);
        if (newNode.type === 'folder') {
          currentLevel = newNode.children!;
        }
      }
    });
  });

  return tree;
};
