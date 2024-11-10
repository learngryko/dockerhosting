import Header from '../components/Header';
import CorsTesting from '../components/CorsTesting';
export default function Home() {
  return (
    <>
      <Header />
      <main>
        <h1>Welcome to the Home Page</h1>
        <p>This is your main content.</p>
        <CorsTesting />
      </main>
    </>
  );
}
