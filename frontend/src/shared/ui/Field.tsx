import { forwardRef, useId, type InputHTMLAttributes, type SelectHTMLAttributes } from 'react';

interface FieldProps {
  label: string;
  error?: string;
  hint?: string;
}

type InputFieldProps = FieldProps & InputHTMLAttributes<HTMLInputElement>;
type SelectFieldProps = FieldProps & SelectHTMLAttributes<HTMLSelectElement>;

function Wrapper({
  id,
  label,
  error,
  hint,
  children,
}: FieldProps & { id: string; children: React.ReactNode }) {
  return (
    <div className="field">
      <label htmlFor={id} className="field__label">
        {label}
      </label>
      {children}
      {hint && !error && <div className="field__hint">{hint}</div>}
      {error && (
        <div className="field__error" role="alert">
          {error}
        </div>
      )}
    </div>
  );
}

export const InputField = forwardRef<HTMLInputElement, InputFieldProps>(function InputField(
  { label, error, hint, ...rest },
  ref,
) {
  const id = useId();
  return (
    <Wrapper id={id} label={label} error={error} hint={hint}>
      <input id={id} ref={ref} className="input" aria-invalid={Boolean(error)} {...rest} />
    </Wrapper>
  );
});

export const SelectField = forwardRef<HTMLSelectElement, SelectFieldProps>(function SelectField(
  { label, error, hint, children, ...rest },
  ref,
) {
  const id = useId();
  return (
    <Wrapper id={id} label={label} error={error} hint={hint}>
      <select id={id} ref={ref} className="input" aria-invalid={Boolean(error)} {...rest}>
        {children}
      </select>
    </Wrapper>
  );
});
