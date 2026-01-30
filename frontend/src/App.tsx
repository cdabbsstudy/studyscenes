import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppShell from './components/layout/AppShell';
import ProjectList from './pages/ProjectList';
import NewProject from './pages/NewProject';
import ProjectWizard from './pages/ProjectWizard';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<Navigate to="/projects" replace />} />
          <Route path="/projects" element={<ProjectList />} />
          <Route path="/projects/new" element={<NewProject />} />
          <Route path="/projects/:id" element={<ProjectWizard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
