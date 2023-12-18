import React, { useState } from 'react';

const Brew = () => {
  const [testName, setTestName] = useState('');

  const handleChange = (event) => {
    setTestName(event.target.value);
  }

  return (
    <div style={{ width: '100%', height: '400px', backgroundColor: 'white', display: 'flex', justifyContent: 'center', alignItems: 'center', borderRadius: '4px', boxSizing: 'border-box', boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)' }}>
      <select value={testName} onChange={handleChange} style={{ width: '200px', padding: '10px', borderRadius: '4px', border: '1px solid #ddd' }}>
        <option value="">Select a test</option>
        <option value="test1">Test 1</option>
        <option value="test2">Test 2</option>
        <option value="test3">Test 3</option>
        <option value="test4">Test 4</option>
      </select>
    </div>
  );
};

export default Brew;
