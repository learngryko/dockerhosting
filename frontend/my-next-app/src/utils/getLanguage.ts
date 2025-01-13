// utils/getLanguage.ts

export const getLanguage = (extension: string): string => {
  const langMap: { [key: string]: string } = {
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.py': 'python',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.cs': 'csharp',
    '.rb': 'ruby',
    '.go': 'go',
    '.php': 'php',
    '.html': 'html',
    '.css': 'css',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.md': 'markdown',
    '.sh': 'shell',
    '.bat': 'batch',
    '.dockerfile': 'dockerfile',
    'Dockerfile': 'dockerfile',
    // Add more mappings as needed
  };

  return langMap[extension.toLowerCase()] || 'plaintext';
};
