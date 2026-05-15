import { useRef, useState } from 'react'

import { Upload } from 'lucide-react'

type Props = {
  onFileSelect: (file: File | null) => void
  accept?: string
  label?: string
  selectedFile?: File | null
}

export function FileUploadButton({ onFileSelect, accept = "image/*", label = "Choose Photo", selectedFile }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleClick = () => {
    inputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null
    onFileSelect(file)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files?.[0] ?? null
    if (file && file.type.startsWith('image/')) {
      onFileSelect(file)
    }
  }

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation()
    onFileSelect(null)
    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

  return (
    <div className="file-upload-wrapper">
      <div
        className={`file-upload-area ${isDragging ? 'dragging' : ''} ${selectedFile ? 'has-file' : ''}`}
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleFileChange}
          className="file-input-hidden"
        />
        {selectedFile ? (
          <div className="file-preview">
            <img src={URL.createObjectURL(selectedFile)} alt="Preview" className="preview-image" />
            <div className="file-info">
              <span className="file-name">{selectedFile.name}</span>
              <button
                type="button"
                className="clear-button"
                onClick={handleClear}
              >
                Remove
              </button>
            </div>
          </div>
        ) : (
          <div className="upload-prompt">
            <Upload size={24} />
            <span>{label}</span>
            <small>or drag and drop</small>
          </div>
        )}
      </div>
    </div>
  )
}