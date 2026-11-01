import { useState } from 'react';
import { logNoApi } from '@/shared/library';
import { Button } from '@/shared/ui';

interface ApkCardProps {
  title: string;
  description: string;
  initialUrl: string;
  placeholder: string;
  action: string;
}

export function ApkCard({ title, description, initialUrl, placeholder, action }: ApkCardProps) {
  const [edited, setEdited] = useState<string | null>(null);
  const url = edited ?? initialUrl;

  const copy = () => {
    void navigator.clipboard?.writeText(url);
  };

  return (
    <section className="card">
      <h2>{title}</h2>
      <p className="muted" style={{ marginBottom: 16 }}>
        {description}
      </p>
      <div className="field">
        <label className="field__label" htmlFor={`${action}-url`}>
          Ссылка на APK
        </label>
        <input
          id={`${action}-url`}
          className="input"
          value={url}
          placeholder={placeholder}
          onChange={(event) => setEdited(event.target.value)}
        />
      </div>
      <div className="btn-row">
        <Button onClick={() => logNoApi(action, { url })}>Обновить ссылку</Button>
        <Button variant="secondary" onClick={copy}>
          Копировать
        </Button>
      </div>
    </section>
  );
}
