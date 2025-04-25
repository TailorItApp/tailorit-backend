# Filesystem API Guide for Frontend

This guide provides instructions on how to use the filesystem API endpoints for building a file management interface.

## Authentication

All API endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### 1. Get Complete Filesystem

```
GET /filesystem
```

Returns the complete filesystem structure including all folders and files in a hierarchical format.

**Response Format:**

```json
{
  "message": "Filesystem fetched successfully",
  "data": {
    "folders": [
      {
        "id": "uuid",
        "name": "folder_name",
        "parent_id": "uuid or null",
        "user_id": "uuid",
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "subfolders": [
          {
            "id": "uuid",
            "name": "subfolder_name",
            "parent_id": "parent_folder_uuid",
            "user_id": "uuid",
            "created_at": "timestamp",
            "updated_at": "timestamp",
            "subfolders": []
          }
        ]
      }
    ],
    "files": [
      {
        "id": "uuid",
        "name": "file_name.tex",
        "storage_path": "path",
        "folder_id": "uuid or null",
        "user_id": "uuid",
        "created_at": "timestamp",
        "updated_at": "timestamp"
      }
    ]
  }
}
```

### 2. File Operations

#### Upload File

```
POST /files
Content-Type: multipart/form-data

file: <file>
folder_id: <optional_uuid>
```

Uploads a new .tex file. The file will be placed in the specified folder if `folder_id` is provided.

#### Download File

```
GET /files/{file_id}/download
```

Returns the content of the file.

#### Get File URL

```
GET /files/{file_id}/url?expires_in=3600
```

Returns a temporary URL to access the file. The URL expires after the specified time (in seconds).

#### Update File

```
PUT /files/{file_id}
Content-Type: application/json

{
    "name": "new_name.tex",
    "folder_id": "new_folder_id"
}
```

Updates file metadata.

#### Delete File

```
DELETE /files/{file_id}
```

Deletes a file.

### 3. Folder Operations

#### Create Folder

```
POST /folders
Content-Type: application/json

{
    "name": "folder_name",
    "parent_id": "optional_parent_folder_id"
}
```

Creates a new folder.

#### Update Folder

```
PUT /folders/{folder_id}
Content-Type: application/json

{
    "name": "new_name",
    "parent_id": "new_parent_id"
}
```

Updates folder metadata.

#### Delete Folder

```
DELETE /folders/{folder_id}
```

Deletes a folder.

## Frontend Implementation Guide

1. **Initial Load**

   - Call `/filesystem` endpoint to get the complete structure
   - The response will include a hierarchical folder structure with nested subfolders
   - Build a tree view using the folders and files data
   - Files in the root level will have `folder_id: null`
   - Files in folders will have their respective `folder_id`

2. **File Operations**

   - For file uploads, use the multipart form data endpoint
   - For file viewing, use the download or URL endpoints
   - Implement drag-and-drop using the update endpoints to change `folder_id`

3. **Folder Operations**

   - Create new folders using the POST endpoint
   - Allow folder renaming using the PUT endpoint
   - Implement folder deletion with confirmation
   - When moving folders, update the `parent_id` using the PUT endpoint

4. **Error Handling**

   - Handle 401 errors for authentication issues
   - Handle 404 errors for not found resources
   - Handle 400 errors for invalid operations
   - Display appropriate error messages to users

5. **Optimization Tips**
   - Cache the filesystem structure locally
   - Only refresh the structure when necessary
   - Use the URL endpoint for large files instead of downloading
   - Implement optimistic updates for better UX

## Example Frontend Code Structure

```typescript
interface File {
  id: string;
  name: string;
  storage_path: string;
  folder_id: string | null;
  user_id: string;
  created_at: string;
  updated_at: string;
}

interface Folder {
  id: string;
  name: string;
  parent_id: string | null;
  user_id: string;
  created_at: string;
  updated_at: string;
  subfolders: Folder[];
}

interface Filesystem {
  folders: Folder[];
  files: File[];
}

// Example API client
class FilesystemAPI {
  async getFilesystem(): Promise<Filesystem> {
    const response = await fetch('/filesystem', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await response.json();
    return data.data;
  }

  async uploadFile(file: File, folderId?: string) {
    const formData = new FormData();
    formData.append('file', file);
    if (folderId) {
      formData.append('folder_id', folderId);
    }

    const response = await fetch('/files', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });
    return response.json();
  }

  // Add other methods for file and folder operations
}

// Example React component for rendering the filesystem
const FileSystemTree: React.FC = () => {
  const [filesystem, setFilesystem] = useState<Filesystem | null>(null);
  const api = new FilesystemAPI();

  useEffect(() => {
    const loadFilesystem = async () => {
      const data = await api.getFilesystem();
      setFilesystem(data);
    };
    loadFilesystem();
  }, []);

  const renderFolder = (folder: Folder) => (
    <div key={folder.id}>
      <div>{folder.name}</div>
      {folder.subfolders.map(renderFolder)}
      {filesystem?.files
        .filter((file) => file.folder_id === folder.id)
        .map((file) => (
          <div key={file.id}>{file.name}</div>
        ))}
    </div>
  );

  return (
    <div>
      {filesystem?.folders.map(renderFolder)}
      {filesystem?.files
        .filter((file) => file.folder_id === null)
        .map((file) => (
          <div key={file.id}>{file.name}</div>
        ))}
    </div>
  );
};
```

## Best Practices

1. **State Management**

   - Keep the filesystem state in a global store
   - Update the state optimistically for better UX
   - Implement proper error handling and rollback

2. **Performance**

   - Implement virtual scrolling for large lists
   - Lazy load file contents
   - Cache file URLs for a reasonable duration

3. **UX Considerations**

   - Show loading states during operations
   - Implement proper error messages
   - Add confirmation dialogs for destructive operations
   - Provide feedback for drag-and-drop operations

4. **Security**
   - Never store JWT tokens in localStorage
   - Implement proper token refresh mechanism
   - Validate file types before upload
   - Sanitize file names and paths
