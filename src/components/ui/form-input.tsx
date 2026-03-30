'use client';

import { ComponentProps } from 'react';

const inputClasses =
  'w-full py-3 bg-transparent border-b border-neon-cyan/15 font-sans text-lg text-text-primary placeholder:text-text-secondary/30 focus:outline-none focus:border-neon-cyan/40 transition-colors min-h-[48px]';

const textareaClasses =
  'w-full p-4 arcane-glass font-sans text-base text-text-primary placeholder:text-text-secondary/30 focus:outline-none focus:border-neon-cyan/30 transition-colors resize-none min-h-[48px]';

const selectClasses =
  'w-full py-3 bg-transparent border-b border-neon-cyan/15 font-sans text-lg text-text-primary focus:outline-none focus:border-neon-cyan/40 transition-colors appearance-none min-h-[48px]';

const labelClasses = 'block font-mono text-[10px] uppercase tracking-[0.2em] text-neon-cyan/70 mb-2';

interface FormInputProps extends Omit<ComponentProps<'input'>, 'id'> {
  label: string;
  id: string;
}

export function FormInput({ label, id, className, ...props }: FormInputProps) {
  return (
    <div>
      <label htmlFor={id} className={labelClasses}>
        {label}
      </label>
      <input id={id} className={`${inputClasses} ${className ?? ''}`} {...props} />
    </div>
  );
}

interface FormTextareaProps extends Omit<ComponentProps<'textarea'>, 'id'> {
  label: string;
  id: string;
}

export function FormTextarea({ label, id, className, ...props }: FormTextareaProps) {
  return (
    <div>
      <label htmlFor={id} className={labelClasses}>
        {label}
      </label>
      <textarea id={id} className={`${textareaClasses} ${className ?? ''}`} {...props} />
    </div>
  );
}

interface FormSelectProps extends Omit<ComponentProps<'select'>, 'id'> {
  label: string;
  id: string;
}

export function FormSelect({ label, id, className, children, ...props }: FormSelectProps) {
  return (
    <div>
      <label htmlFor={id} className={labelClasses}>
        {label}
      </label>
      <select id={id} className={`${selectClasses} ${className ?? ''}`} {...props}>
        {children}
      </select>
    </div>
  );
}
