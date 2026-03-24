import { ComponentProps } from 'react';

const baseClasses =
  'w-full px-4 py-3.5 bg-surface-0 border border-white/10 rounded-xl font-mono text-sm text-white placeholder:text-white/15 focus:outline-none focus:border-white/40 focus:ring-1 focus:ring-white/10 transition-colors min-h-[48px]';

const labelClasses = 'block text-xs text-white/30 font-mono mb-1.5 uppercase tracking-wider';

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
      <input id={id} className={`${baseClasses} ${className ?? ''}`} {...props} />
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
      <textarea id={id} className={`${baseClasses} resize-none ${className ?? ''}`} {...props} />
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
      <select id={id} className={`${baseClasses} appearance-none ${className ?? ''}`} {...props}>
        {children}
      </select>
    </div>
  );
}
