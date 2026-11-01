export const EVENT_TYPES = [
  'admin_login_failed',
  'consent_revoked',
  'unknown_uid',
  'invalid_signature',
  'expired_timestamp',
  'duplicate_check_in',
  'unknown_device',
  'device_revoked',
  'enroll_code_invalid',
] as const;

export const EVENT_DESCRIPTIONS: Record<string, string> = {
  admin_login_failed: 'Неудачная попытка входа администратора',
  consent_revoked: 'Согласие студента отозвано',
  unknown_uid: 'Карта не найдена в students',
  invalid_signature: 'Подпись запроса не совпала',
  expired_timestamp: 'Метка времени запроса устарела',
  duplicate_check_in: 'Повторный check_in без check_out',
  unknown_device: 'Устройство не найдено в БД',
  device_revoked: 'Запрос от отозванного устройства',
  enroll_code_invalid: 'Неверный или просроченный код регистрации',
};
