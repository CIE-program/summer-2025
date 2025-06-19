import React from 'react';

interface FormFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  maxLength?: number;
  error?: string;
  required?: boolean;
  type?: string;
  textarea?: boolean;
  rows?: number;
}

const FormField: React.FC<FormFieldProps> = ({
  label,
  value,
  onChange,
  placeholder,
  maxLength,
  error,
  required,
  type = 'text',
  textarea = false,
  rows = 3
}) => {
  const inputClassName = `w-full px-4 py-3 border ${
    error ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
  } rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-opacity-50 transition-colors duration-200`;

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {textarea ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          maxLength={maxLength}
          rows={rows}
          className={inputClassName}
        />
      ) : (
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          maxLength={maxLength}
          className={inputClassName}
        />
      )}
      
      <div className="flex justify-between items-center">
        {error && (
          <p className="text-sm text-red-600">{error}</p>
        )}
        {maxLength && (
          <p className="text-xs text-gray-500 ml-auto">
            {value.length}/{maxLength}
          </p>
        )}
      </div>
    </div>
  );
};

export default FormField;