import type { IconName } from '@/shared/ui';

export interface NavItem {
  to: string;
  label: string;
  icon: IconName;
}

export const NAV_ITEMS: NavItem[] = [
  { to: '/students', label: 'Студенты', icon: 'users' },
  { to: '/codes', label: 'Коды регистрации', icon: 'key' },
  { to: '/devices', label: 'Устройства', icon: 'phone' },
  { to: '/events', label: 'Журнал событий', icon: 'list' },
  { to: '/apk', label: 'Приложение (APK)', icon: 'download' },
];

export const PASSWORD_ITEM: NavItem = { to: '/password', label: 'Смена пароля', icon: 'lock' };
