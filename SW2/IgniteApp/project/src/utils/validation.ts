export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@.*pes\.edu$/i;
  return emailRegex.test(email.toLowerCase());
};

export const validateRequiredFields = (fields: Record<string, string>): Record<string, string> => {
  const errors: Record<string, string> = {};
  
  Object.entries(fields).forEach(([key, value]) => {
    if (!value.trim()) {
      errors[key] = `${key.replace(/([A-Z])/g, ' $1').toLowerCase()} is required`;
    }
  });
  
  return errors;
};

export const validateCharacterLimit = (value: string, limit: number, fieldName: string): string | null => {
  if (value.length > limit) {
    return `${fieldName} must be ${limit} characters or less`;
  }
  return null;
};