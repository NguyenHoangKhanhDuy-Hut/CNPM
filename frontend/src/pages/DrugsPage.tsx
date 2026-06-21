import { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import DrugCard from '@/components/DrugCard';
import client from '@/lib/client';

const DrugsPage = () => {
  const [drugs, setDrugs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('');

  useEffect(() => {
    const fetchDrugs = async () => {
      try {
        const response = await client.entities.drugs.query({ limit: 100 });
        setDrugs(response.data?.items || []);
      } catch (err) {
        console.error('Failed to fetch drugs:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDrugs();
  }, []);

  const groups = [...new Set(drugs.map((d) => d.group_name).filter(Boolean))];

  const filteredDrugs = drugs.filter((drug) => {
    const matchesSearch =
      !searchQuery ||
      drug.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      drug.code?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      drug.manufacturer?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesGroup = !selectedGroup || drug.group_name === selectedGroup;
    return matchesSearch && matchesGroup;
  });

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-900">Danh mục thuốc</h1>
          <p className="text-slate-500 text-sm mt-1">Tra cứu thông tin chi tiết về các loại thuốc</p>
        </div>

        {/* Search & Filter */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm kiếm thuốc theo tên, mã, nhà sản xuất..."
              className="w-full h-12 pl-11 pr-4 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            />
          </div>
          <select
            value={selectedGroup}
            onChange={(e) => setSelectedGroup(e.target.value)}
            className="h-12 px-4 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Tất cả nhóm</option>
            {groups.map((g) => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>
        </div>

        {/* Results */}
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
          </div>
        ) : filteredDrugs.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-2xl border border-slate-200">
            <Search className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900 mb-2">Không tìm thấy thuốc</h3>
            <p className="text-sm text-slate-500">Thử thay đổi từ khóa tìm kiếm</p>
          </div>
        ) : (
          <>
            <p className="text-sm text-slate-500 mb-4">
              Tìm thấy <span className="font-semibold text-slate-900">{filteredDrugs.length}</span> loại thuốc
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredDrugs.map((drug) => (
                <DrugCard key={drug.id} drug={drug} />
              ))}
            </div>
          </>
        )}
      </div>
      <Footer />
    </div>
  );
};

export default DrugsPage;