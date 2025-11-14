import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { Upload, File, Image, Video, Music } from 'lucide-react';
import './FileUpload.css';

const API_URL = 'http://localhost:8000';

interface FileUploadProps {
  onAnalysisComplete: (result: any) => void;
  onAnalysisStart: () => void;
  onError: (error: string) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onAnalysisComplete,
  onAnalysisStart,
  onError,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
      'video/*': ['.mp4', '.avi', '.mov', '.mkv'],
      'audio/*': ['.mp3', '.wav', '.ogg', '.m4a'],
    },
    multiple: false,
  });

  const getFileType = (file: File): 'image' | 'video' | 'audio' => {
    if (file.type.startsWith('image/')) return 'image';
    if (file.type.startsWith('video/')) return 'video';
    if (file.type.startsWith('audio/')) return 'audio';
    return 'image';
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    onAnalysisStart();

    try {
      const fileType = getFileType(selectedFile);
      const formData = new FormData();
      formData.append('file', selectedFile);

      const endpoint = `${API_URL}/api/analyze/${fileType}`;
      const response = await axios.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      onAnalysisComplete(response.data);
      setSelectedFile(null);
    } catch (error: any) {
      console.error('Analysis error:', error);
      onError(
        error.response?.data?.detail ||
          'Failed to analyze file. Please try again.'
      );
    }
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) return <Image size={24} />;
    if (file.type.startsWith('video/')) return <Video size={24} />;
    if (file.type.startsWith('audio/')) return <Music size={24} />;
    return <File size={24} />;
  };

  return (
    <div className="file-upload-container">
      <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
        <input {...getInputProps()} />
        <Upload size={48} className="upload-icon" />
        {isDragActive ? (
          <p className="dropzone-text">Drop the file here...</p>
        ) : (
          <>
            <p className="dropzone-text">
              Drag & drop a file here, or click to select
            </p>
            <p className="dropzone-hint">
              Supported: Images (JPG, PNG), Videos (MP4, AVI, MOV), Audio (MP3, WAV)
            </p>
          </>
        )}
      </div>

      {selectedFile && (
        <div className="selected-file">
          <div className="file-info">
            {getFileIcon(selectedFile)}
            <div className="file-details">
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
          </div>
          <button className="analyze-button" onClick={handleAnalyze}>
            Analyze File
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
