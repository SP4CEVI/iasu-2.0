import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { ApkPage } from '@/features/apk';
import { AuthProvider, ChangePasswordPage, LoginPage, RequireAuth } from '@/features/auth';
import { CodesPage } from '@/features/codes';
import { DevicesPage } from '@/features/devices';
import { EventsPage } from '@/features/events';
import { ActPage, StudentsPage } from '@/features/students';
import { AppLayout } from '@/layout';

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<RequireAuth />}>
            <Route element={<AppLayout />}>
              <Route index element={<Navigate to="/students" replace />} />
              <Route path="/students" element={<StudentsPage />} />
              <Route path="/students/:id/act" element={<ActPage />} />
              <Route path="/codes" element={<CodesPage />} />
              <Route path="/devices" element={<DevicesPage />} />
              <Route path="/events" element={<EventsPage />} />
              <Route path="/apk" element={<ApkPage />} />
              <Route path="/password" element={<ChangePasswordPage />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
