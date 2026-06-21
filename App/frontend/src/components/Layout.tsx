import { ReactNode } from 'react';

import Header from './Header';
import Footer from './Footer';

type Props = {
  children: ReactNode;
};

const Layout = ({ children }: Props) => {
  return (

<div className="min-h-screen flex flex-col bg-slate-50">

  <Header />

  <main className="flex-1">

    {children}

  </main>

  <Footer />

</div>

  );
};

export default Layout;