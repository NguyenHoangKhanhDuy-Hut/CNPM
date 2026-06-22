import { Toaster } from '@/components/ui/sonner';
import { TooltipProvider } from '@/components/ui/tooltip';
import { ThemeProvider } from 'next-themes';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';
import ProtectedAdminRoute from '@/components/ProtectedAdminRoute';
import ProtectedRoute from '@/components/ProtectedRoute';
import ChatBot from '@/components/ChatBot';
import Index from './pages/Index';
import SearchPage from './pages/SearchPage';
import PredictPage from './pages/PredictPage';
import DiseaseDetailPage from './pages/DiseaseDetailPage';
import DrugDetailPage from './pages/DrugDetailPage';
import DrugsPage from './pages/DrugsPage';
import AdminDashboard from './pages/AdminDashboard';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import AccountPage from './pages/AccountPage';

const queryClient = new QueryClient();

const AppRoutes = () => (
  <Routes>
    <Route path="/" element={<Index />} />
    <Route path="/search" element={<SearchPage />} />
    <Route path="/predict" element={<PredictPage />} />
    <Route path="/disease/:id" element={<DiseaseDetailPage />} />
    <Route path="/drug/:id" element={<DrugDetailPage />} />
    <Route path="/drugs" element={<DrugsPage />} />
    <Route path="/admin" element={<ProtectedAdminRoute><AdminDashboard /></ProtectedAdminRoute>} />
    <Route path="/account" element={<ProtectedRoute><AccountPage /></ProtectedRoute>} />
    <Route path="/login" element={<LoginPage />} />
    <Route path="/register" element={<RegisterPage />} />
  </Routes>
);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <TooltipProvider>
        <Toaster />
        <BrowserRouter>
          <AuthProvider>
            <AppRoutes />
            <ChatBot />
          </AuthProvider>
        </BrowserRouter>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
export { AppRoutes };