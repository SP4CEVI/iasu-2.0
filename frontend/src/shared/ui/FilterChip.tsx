interface FilterChipProps {
  text: string;
  onClear: () => void;
}

export function FilterChip({ text, onClear }: FilterChipProps) {
  return (
    <div className="chip">
      <span>{text}</span>
      <button type="button" onClick={onClear}>
        Показать все
      </button>
    </div>
  );
}