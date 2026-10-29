import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { DataTable } from '@/components/common/data-table';
import { useOrgs } from '@/hooks/use-orgs';

// 机构管理页，page id: orgs
export function OrgsPage() {
  const { data, loading } = useOrgs();
  return (
    <div className="space-y-4">
      <h1 className="text-xl">机构管理</h1>
      <form className="flex gap-2">
        <Input placeholder="机构名称" />
        <Select options={['全部状态', '正常', '已停用']} />
        <Button>查询</Button>
        <Button variant="outline">重置</Button>
      </form>
      <DataTable
        loading={loading}
        rows={data}
        columns={[
          { key: 'name', title: '机构名称' },
          { key: 'creditCode', title: '统一社会信用代码' },
          { key: 'status', title: '状态', render: (s) => <span className="rounded-md bg-primary/10">{s}</span> },
        ]}
        actions={[{ label: '查看' }, { label: '停用' }]}
      />
    </div>
  );
}
