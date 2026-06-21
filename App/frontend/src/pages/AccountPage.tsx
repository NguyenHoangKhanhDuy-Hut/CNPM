import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { format } from 'date-fns';
import { vi } from 'date-fns/locale';
import { User, Mail, Shield, Calendar, LogOut, Save, Loader2, Bookmark, Trash2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/client';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const roleLabels: Record<string, string> = {
  admin: 'Quản trị viên',
  user: 'Người dùng',
};

const roleColors: Record<string, string> = {
  admin: 'bg-red-100 text-red-700 border-red-200',
  user: 'bg-blue-100 text-blue-700 border-blue-200',
};

const AccountPage = () => {
  const { user, logout, refetch } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState(user?.name || '');
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [savedDrugs, setSavedDrugs] = useState<any[]>([]);

  useEffect(() => {
    const fetchSavedDrugs = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) return;
        const res = await api.get('/api/v1/user/saved-drugs');
        setSavedDrugs(res.data?.items || []);
      } catch (err) {
        console.error('Failed to fetch saved drugs:', err);
      }
    };
    fetchSavedDrugs();
  }, []);

  const handleUnsave = async (drugId: number) => {
    try {
      await api.delete(`/api/v1/user/saved-drugs/${drugId}`);
      setSavedDrugs((prev) => prev.filter((item) => item.drug_id !== drugId));
    } catch {
      console.error('Failed to unsave drug');
    }
  };

  const handleSaveName = async () => {
    if (!name.trim() || name === user?.name) return;
    setSaving(true);
    setSuccess('');
    try {
      await api.put('/api/v1/auth/me', { name: name.trim() });
      await refetch();
      setSuccess('Cập nhật thành công');
      setTimeout(() => setSuccess(''), 3000);
    } catch {
      setSuccess('');
    } finally {
      setSaving(false);
    }
  };

  const initials = (user?.name || user?.email || '?')
    .charAt(0)
    .toUpperCase();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Header />
      <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-8">
        <h1 className="text-2xl font-bold text-slate-900 mb-6">
          Thông tin tài khoản
        </h1>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-4">
                <Avatar className="h-16 w-16">
                  <AvatarFallback className="bg-blue-600 text-white text-lg">
                    {initials}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <CardTitle className="text-lg">
                    {user?.name || 'Chưa có tên'}
                  </CardTitle>
                  <p className="text-sm text-slate-500">{user?.email}</p>
                </div>
              </div>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Chi tiết tài khoản</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3 text-sm">
                <Mail className="h-4 w-4 text-slate-400" />
                <span className="text-slate-600">Email:</span>
                <span className="font-medium text-slate-900">{user?.email}</span>
              </div>

              <div className="flex items-center gap-3 text-sm">
                <Shield className="h-4 w-4 text-slate-400" />
                <span className="text-slate-600">Vai trò:</span>
                <Badge
                  variant="outline"
                  className={`font-medium ${roleColors[user?.role || 'user']}`}
                >
                  {roleLabels[user?.role || 'user']}
                </Badge>
              </div>

              {user?.last_login && (
                <div className="flex items-center gap-3 text-sm">
                  <Calendar className="h-4 w-4 text-slate-400" />
                  <span className="text-slate-600">Lần đăng nhập cuối:</span>
                  <span className="font-medium text-slate-900">
                    {format(new Date(user.last_login), 'HH:mm - dd/MM/yyyy', { locale: vi })}
                  </span>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Chỉnh sửa thông tin</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Tên hiển thị</Label>
                <div className="flex gap-2">
                  <Input
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Nhập tên của bạn"
                  />
                  <Button
                    onClick={handleSaveName}
                    disabled={saving || !name.trim() || name === user?.name}
                  >
                    {saving ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4" />
                    )}
                    Lưu
                  </Button>
                </div>
                {success && (
                  <p className="text-sm text-green-600">{success}</p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Bookmark className="h-4 w-4 text-blue-600" />
                Thuốc đã lưu
              </CardTitle>
            </CardHeader>
            <CardContent>
              {savedDrugs.length === 0 ? (
                <p className="text-sm text-slate-500">Chưa có thuốc nào được lưu</p>
              ) : (
                <div className="space-y-2">
                  {savedDrugs.map((item) => (
                    <div key={item.id} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                      <Link
                        to={`/drug/${item.drug_id}`}
                        className="text-sm font-medium text-blue-600 hover:underline"
                      >
                        {item.drug_name || `Thuốc #${item.drug_id}`}
                      </Link>
                      <button
                        onClick={() => handleUnsave(item.drug_id)}
                        className="text-slate-400 hover:text-red-500 transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base text-red-600">
                Phiên đăng nhập
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Button
                variant="outline"
                className="w-full border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700"
                onClick={() => { logout(); navigate('/'); }}
              >
                <LogOut className="h-4 w-4 mr-2" />
                Đăng xuất
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default AccountPage;
