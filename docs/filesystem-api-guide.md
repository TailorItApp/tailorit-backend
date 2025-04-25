# Filesystem API Guide with SWR

This guide provides detailed instructions for implementing a dynamic filesystem interface using the API with SWR for data fetching and caching.

## Table of Contents

- [API Overview](#api-overview)
- [Authentication](#authentication)
- [Filesystem Structure](#filesystem-structure)
- [API Endpoints and SWR Implementation](#api-endpoints-and-swr-implementation)
- [Error Handling](#error-handling)
- [Implementation Tips](#implementation-tips)
- [Example Implementation](#example-implementation)

## API Overview

The API is structured around three main resources:

1. Files (`/api/v1/files`)
2. Folders (`/api/v1/folders`)
3. Filesystem (`/api/v1/filesystem`)

All endpoints require JWT authentication, which should be included in the Authorization header as a Bearer token.

## Authentication

Before making any API calls, ensure you have a valid JWT token. Create a custom hook for handling authentication:

```typescript
// hooks/useAuth.ts
import { useSession } from 'next-auth/react';

export const useAuth = () => {
  const { data: session } = useSession();
  return {
    token: session?.accessToken,
    headers: {
      Authorization: `Bearer ${session?.accessToken}`,
      'Content-Type': 'application/json',
    },
  };
};
```

## Filesystem Structure

The filesystem is organized hierarchically:

- Root level can contain both files and folders
- Folders can contain subfolders and files
- Files can only exist at the root level or within folders

## API Endpoints and SWR Implementation

### 1. Getting the Complete Filesystem

```typescript
// hooks/useFilesystem.ts
import useSWR from 'swr';
import { useAuth } from './useAuth';

const fetcher = (url: string, headers: any) =>
  fetch(url, { headers }).then((res) => res.json());

export const useFilesystem = () => {
  const { headers } = useAuth();
  const { data, error, mutate } = useSWR(
    ['/api/v1/filesystem', headers],
    ([url, headers]) => fetcher(url, headers)
  );

  return {
    filesystem: data?.data,
    isLoading: !error && !data,
    isError: error,
    mutate,
  };
};
```

### 2. Folder Operations

```typescript
// hooks/useFolders.ts
import useSWR from 'swr';
import { useAuth } from './useAuth';

export const useFolders = (parentId?: string) => {
  const { headers } = useAuth();
  const { data, error, mutate } = useSWR(
    parentId
      ? [`/api/v1/folders?parent_id=${parentId}`, headers]
      : ['/api/v1/folders', headers],
    ([url, headers]) => fetcher(url, headers)
  );

  const createFolder = async (name: string, parentId?: string) => {
    const response = await fetch('/api/v1/folders', {
      method: 'POST',
      headers,
      body: JSON.stringify({ name, parent_id: parentId }),
    });
    await mutate();
    return response.json();
  };

  const updateFolder = async (
    folderId: string,
    updates: { name?: string; parent_id?: string }
  ) => {
    const response = await fetch(`/api/v1/folders/${folderId}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(updates),
    });
    await mutate();
    return response.json();
  };

  const deleteFolder = async (folderId: string) => {
    const response = await fetch(`/api/v1/folders/${folderId}`, {
      method: 'DELETE',
      headers,
    });
    await mutate();
    return response.json();
  };

  return {
    folders: data?.data,
    isLoading: !error && !data,
    isError: error,
    createFolder,
    updateFolder,
    deleteFolder,
    mutate,
  };
};
```

### 3. File Operations

```typescript
// hooks/useFiles.ts
import useSWR from 'swr';
import { useAuth } from './useAuth';

export const useFiles = (folderId?: string) => {
  const { headers } = useAuth();
  const { data, error, mutate } = useSWR(
    folderId
      ? [`/api/v1/files?folder_id=${folderId}`, headers]
      : ['/api/v1/files', headers],
    ([url, headers]) => fetcher(url, headers)
  );

  const uploadFile = async (file: File, name?: string, folderId?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (name) formData.append('name', name);
    if (folderId) formData.append('folder_id', folderId);

    const response = await fetch('/api/v1/files', {
      method: 'POST',
      headers: {
        Authorization: headers['Authorization'],
      },
      body: formData,
    });
    await mutate();
    return response.json();
  };

  const updateFile = async (
    fileId: string,
    updates: { name?: string; folder_id?: string }
  ) => {
    const formData = new FormData();
    if (updates.name) formData.append('name', updates.name);
    if (updates.folder_id) formData.append('folder_id', updates.folder_id);

    const response = await fetch(`/api/v1/files/${fileId}`, {
      method: 'PUT',
      headers: {
        Authorization: headers['Authorization'],
      },
      body: formData,
    });
    await mutate();
    return response.json();
  };

  const deleteFile = async (fileId: string) => {
    const response = await fetch(`/api/v1/files/${fileId}`, {
      method: 'DELETE',
      headers,
    });
    await mutate();
    return response.json();
  };

  const downloadFile = async (fileId: string) => {
    const response = await fetch(`/api/v1/files/${fileId}/download`, {
      headers,
    });
    return response.blob();
  };

  const getFileUrl = async (fileId: string, expiresIn: number = 3600) => {
    const response = await fetch(
      `/api/v1/files/${fileId}/url?expires_in=${expiresIn}`,
      {
        headers,
      }
    );
    const data = await response.json();
    return data.data.url;
  };

  return {
    files: data?.data,
    isLoading: !error && !data,
    isError: error,
    uploadFile,
    updateFile,
    deleteFile,
    downloadFile,
    getFileUrl,
    mutate,
  };
};
```

## Error Handling

SWR provides built-in error handling, but you can create a custom error boundary component:

```typescript
// components/ErrorBoundary.tsx
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
          >
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## Implementation Tips

1. **Optimistic Updates**:

   ```typescript
   const updateFolder = async (
     folderId: string,
     updates: { name?: string }
   ) => {
     // Optimistically update the UI
     const optimisticData = folders.map((folder) =>
       folder.id === folderId ? { ...folder, ...updates } : folder
     );
     mutate(optimisticData, false);

     try {
       await api.updateFolder(folderId, updates);
       mutate(); // Revalidate
     } catch (error) {
       mutate(); // Revert on error
       throw error;
     }
   };
   ```

2. **Loading States**:

   ```typescript
   const { data, isLoading } = useFilesystem();
   if (isLoading) return <LoadingSpinner />;
   ```

3. **Error States**:
   ```typescript
   const { data, isError } = useFilesystem();
   if (isError) return <ErrorMessage />;
   ```

## Example Implementation

```typescript
// components/FileSystem.tsx
import { useState } from 'react';
import { useFilesystem } from '../hooks/useFilesystem';
import { useFolders } from '../hooks/useFolders';
import { useFiles } from '../hooks/useFiles';

export const FileSystem = () => {
  const [currentPath, setCurrentPath] = useState<string[]>([]);
  const { filesystem, isLoading, mutate } = useFilesystem();
  const { createFolder, updateFolder, deleteFolder } = useFolders();
  const { uploadFile, updateFile, deleteFile } = useFiles();

  const handleCreateFolder = async (name: string) => {
    const currentFolderId = currentPath[currentPath.length - 1];
    await createFolder(name, currentFolderId);
  };

  const handleFileUpload = async (file: File) => {
    const currentFolderId = currentPath[currentPath.length - 1];
    await uploadFile(file, file.name, currentFolderId);
  };

  const handleDragDrop = async (
    sourceId: string,
    targetId: string,
    type: 'file' | 'folder'
  ) => {
    if (type === 'file') {
      await updateFile(sourceId, { folder_id: targetId });
    } else {
      await updateFolder(sourceId, { parent_id: targetId });
    }
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="filesystem">
      <Breadcrumb path={currentPath} />
      <FileList
        files={filesystem?.files || []}
        folders={filesystem?.folders || []}
        onFileClick={handleFileClick}
        onFolderClick={handleFolderClick}
        onDragDrop={handleDragDrop}
      />
      <ContextMenu />
    </div>
  );
};
```

## Type Definitions

```typescript
// types/filesystem.ts
export interface File {
  id: string;
  name: string;
  storage_path: string;
  folder_id: string | null;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface Folder {
  id: string;
  name: string;
  parent_id: string | null;
  user_id: string;
  created_at: string;
  updated_at: string;
  subfolders: Folder[];
  files: File[];
}

export interface Filesystem {
  folders: Folder[];
  files: File[];
}

export interface ApiResponse<T> {
  message: string;
  data: T;
}

export interface ApiError {
  message: string;
  details?: {
    error?: string;
    error_code?: string;
    [key: string]: any;
  };
}
```

## Best Practices

1. **SWR Configuration**:

   ```typescript
   // _app.tsx
   import { SWRConfig } from 'swr';

   function MyApp({ Component, pageProps }) {
     return (
       <SWRConfig
         value={{
           refreshInterval: 3000,
           revalidateOnFocus: false,
           dedupingInterval: 2000,
         }}
       >
         <Component {...pageProps} />
       </SWRConfig>
     );
   }
   ```

2. **Prefetching**:

   ```typescript
   // Prefetch folder contents when hovering
   const prefetchFolder = (folderId: string) => {
     mutate([`/api/v1/folders?parent_id=${folderId}`, headers]);
   };
   ```

3. **Infinite Loading**:

   ```typescript
   const { data, size, setSize } = useSWRInfinite(
     (index) => [`/api/v1/files?page=${index + 1}`, headers],
     fetcher
   );
   ```

4. **Error Retry**:
   ```typescript
   const { data, error } = useSWR('/api/v1/filesystem', fetcher, {
     onErrorRetry: (error, key, config, revalidate, { retryCount }) => {
       if (retryCount >= 3) return;
       setTimeout(() => revalidate({ retryCount }), 5000);
     },
   });
   ```

This implementation provides a solid foundation for building a dynamic filesystem interface with SWR. The hooks can be extended with additional features like search, sorting, and filtering as needed.
