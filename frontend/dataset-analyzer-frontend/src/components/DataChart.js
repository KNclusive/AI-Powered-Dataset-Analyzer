import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import Typography from '@mui/material/Typography';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';

const DataComparisonChart = ({ data1, data2 }) => {
  const [xKey, setXKey] = useState('');
  const [yKey, setYKey] = useState('');
  

  // Get common keys
  const commonKeys = data1.length > 0 && data2.length > 0
    ? Object.keys(data1[0]).filter((key) => key in data2[0])
    : [];

  const numericKeys = commonKeys.filter(
    (key) => !isNaN(parseFloat(data1[0][key])) && !isNaN(parseFloat(data2[0][key]))
  );

  const handleXKeyChange = (event) => {
    setXKey(event.target.value);
  };

  const handleYKeyChange = (event) => {
    setYKey(event.target.value);
  };

  // Combine data for comparison when keys are selected
  const combinedData =
    xKey && yKey
      ? data1.map((item, index) => ({
          name: item[xKey] || `Item ${index + 1}`,
          Dataset1: parseFloat(item[yKey]) || 0,
          Dataset2: data2[index] ? parseFloat(data2[index][yKey]) || 0 : 0,
        }))
      : [];

  return (
    <div style={{ marginTop: 20 }}>
      <Typography variant="h5" sx={{ color: 'primary.main' }}>
        Dataset Comparison
      </Typography>
      <div style={{ marginTop: 10, display: 'flex', alignItems: 'center' }}>
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel sx={{ color: '#b0bec5' }}>X-Axis</InputLabel>
          <Select
            value={xKey}
            onChange={handleXKeyChange}
            label="X-Axis"
            sx={{
              color: '#ffffff',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#b0bec5',
              },
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: '#ffffff',
              },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: '#00e5ff',
              },
              '& .MuiSvgIcon-root': {
                color: '#ffffff',
              },
            }}
          >
            {commonKeys.map((key) => (
              <MenuItem key={key} value={key}>
                {key}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl sx={{ minWidth: 120, marginLeft: 2 }}>
          <InputLabel sx={{ color: '#b0bec5' }}>Y-Axis</InputLabel>
          <Select
            value={yKey}
            onChange={handleYKeyChange}
            label="Y-Axis"
            sx={{
              color: '#ffffff',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#b0bec5',
              },
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: '#ffffff',
              },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: '#00e5ff',
              },
              '& .MuiSvgIcon-root': {
                color: '#ffffff',
              },
            }}
          >
            {numericKeys.map((key) => (
              <MenuItem key={key} value={key}>
                {key}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </div>
      {xKey && yKey && (
        <div style={{ width: '100%', height: 300, marginTop: 20 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={combinedData}>
              <CartesianGrid stroke="#555" />
              <XAxis dataKey="name" stroke="#ffffff" />
              <YAxis stroke="#ffffff" />
              <Tooltip
                contentStyle={{ backgroundColor: '#333', borderColor: '#777' }}
                itemStyle={{ color: '#ffffff' }}
                labelStyle={{ color: '#ffffff' }}
              />
              <Legend
                wrapperStyle={{ color: '#ffffff' }}
                iconType="circle"
                align="right"
                verticalAlign="top"
              />
              <Bar dataKey="Dataset1" fill="#ff4081" name="Dataset 1" />
              <Bar dataKey="Dataset2" fill="#7c4dff" name="Dataset 2" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default DataComparisonChart;