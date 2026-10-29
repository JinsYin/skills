import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { DataTable } from '@/components/common/data-table';
import { useApps } from '@/hooks/use-apps';
import { useOrgOptions } from '@/hooks/use-orgs';

// 应用管理页，page id: apps
export function AppsPage() {
  const { data, loading } = useApps();
  const orgOptions = useOrgOptions();
  return (
    <div className="space-y-4">
      <h1 className="text-xl">应用管理</h1>
      <form className="flex gap-2">
        <Input placeholder="应用名称" />
        <Select options={['全部机构', ...orgOptions]} />
        <Select options={['全部状态', '启用', '停用']} />
        <Button>查询</Button>
        <Button variant="outline">重置</Button>
        <Button className="bg-primary text-primary-foreground">新建应用</Button>
      </form>
      <DataTable
        loading={loading}
        rows={data}
        columns={[
          { key: 'name', title: '应用名称' },
          { key: 'orgName', title: '所属机构' },
          { key: 'appKey', title: 'AppKey', masked: true },
          { key: 'status', title: '状态' },
          { key: 'createdAt', title: '创建时间' },
        ]}
        actions={[
          { label: '编辑' },
          { label: '重置密钥', confirm: true },
          { label: '停用', confirm: true },
        ]}
      />
    </div>
  );
}
