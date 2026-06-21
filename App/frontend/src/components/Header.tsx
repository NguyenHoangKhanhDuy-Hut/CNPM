import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {Activity,Menu,X,LogOut,User,Bot} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuth();

 const navLinks = [
  { label: 'Trang chủ', path: '/' },

  { label: 'Tra cứu bệnh', path: '/search' },

  { label: 'Thuốc', path: '/drugs' },

  { label: 'Dự đoán AI', path: '/predict' },

  { label: '🤖 MediPredict AI', path: '/ai-chat' },
];
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Activity className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold text-slate-900">
              Medi<span className="text-blue-600">Predict</span>
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  location.pathname === link.path
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <>
                <Link
                  to="/admin"
                  className="px-3 py-2 text-xs font-medium border border-slate-200 text-slate-500 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Admin
                </Link>
                <Link
                  to="/account"
                  className="flex items-center gap-2 px-3 py-1.5 bg-slate-50 rounded-lg text-sm text-slate-600 hover:bg-blue-50 hover:text-blue-700 transition-colors"
                >
                  <User className="h-4 w-4" />
                  {user.name || user.email}
                </Link>
                <button
                  onClick={logout}
                  className="px-3 py-2 text-sm font-medium text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors flex items-center gap-1"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
                >
                  Đăng nhập
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Đăng ký
                </Link>
              </>
            )}
          </div>

          <button
            className="md:hidden p-2 text-slate-700 hover:text-blue-600"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden pb-4 border-t border-slate-200">
            <nav className="flex flex-col gap-1 pt-3">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    location.pathname === link.path
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-slate-700 hover:bg-slate-50'
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {link.label}
                </Link>
              ))}
            </nav>
            <div className="flex flex-col gap-2 mt-3 px-3">
              {user ? (
                <>
                  <Link
                    to="/account"
                    onClick={() => setMobileMenuOpen(false)}
                    className="px-3 py-2 text-sm text-slate-500 hover:text-blue-600"
                  >
                    {user.name || user.email}
                  </Link>
                  <button
                    onClick={() => { logout(); setMobileMenuOpen(false); }}
                    className="w-full py-2.5 border border-slate-200 rounded-lg text-sm font-medium text-red-600"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    onClick={() => setMobileMenuOpen(false)}
                    className="w-full py-2.5 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 text-center block"
                  >
                    Đăng nhập
                  </Link>
                  <Link
                    to="/register"
                    onClick={() => setMobileMenuOpen(false)}
                    className="w-full py-2.5 bg-blue-600 rounded-lg text-sm font-medium text-white text-center block"
                  >
                    Đăng ký
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;