import React, { useState, useMemo, useEffect } from 'react';
import { fetchDataset } from '../services/api';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  TableSortLabel
} from '@mui/material';
import { styled } from '@mui/material/styles';
import Loader from './Loader';

const StyledPaper = styled(Paper)(({ theme }) => ({
  backgroundColor: '#ffffff',
  color: '#000000',
  width: '100%',
  overflow: 'hidden',
  '& .MuiTypography-root': {
    color: '#000000',
  },
}));

const StyledTableCell = styled(TableCell)(({ theme }) => ({
  borderRight: `1px solid #e0e0e0`,
  borderBottom: `1px solid #e0e0e0`,
  color: '#000000',
  padding: '8px',
  '&:last-child': {
    borderRight: 0,
  },
}));

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  '&:nth-of-type(odd)': {
    backgroundColor: '#f5f5f5',
  },
  '&:hover': {
    backgroundColor: '#e0e0e0',
  },
}));

const DatasetTable = ({ datasetName }) => {
  const [dataset, setDataset] = useState([]);
  const [orderBy, setOrderBy] = useState('');
  const [order, setOrder] = useState('asc');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchDataset(datasetName);
        setDataset(data);
        setError(null); // Reset error state
      } catch (error) {
        console.error('Failed to load dataset:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [datasetName]);

  const headers = useMemo(
    () => (dataset && dataset.length > 0 ? Object.keys(dataset[0]) : []),
    [dataset]
  );

  const sortedData = useMemo(() => {
    if (!dataset || dataset.length === 0 || !orderBy) return dataset;
    return [...dataset].sort((a, b) => {
      if (a[orderBy] < b[orderBy]) return order === 'asc' ? -1 : 1;
      if (a[orderBy] > b[orderBy]) return order === 'asc' ? 1 : -1;
      return 0;
    });
  }, [dataset, order, orderBy]);

  const handleSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  if (loading) {
    return (
      <StyledPaper elevation={3}>
        <Typography variant="h6" sx={{ p: 1, backgroundColor: '#e0e0e0' }}>
          {datasetName}
        </Typography>
        <Loader />  {/* Use Loader instead of plain text */}
      </StyledPaper>
    );
  }

  if (error) {
    return (
      <StyledPaper elevation={3}>
        <Typography variant="h6" sx={{ p: 1, backgroundColor: '#e0e0e0' }}>
          {datasetName}
        </Typography>
        <Typography sx={{ p: 2 }}>Error: {error}</Typography>
      </StyledPaper>
    );
  }

  if (!dataset || dataset.length === 0) {
    return (
      <StyledPaper elevation={3}>
        <Typography variant="h6" sx={{ p: 1, backgroundColor: '#e0e0e0', borderBottom: '1px solid #bdbdbd' }}>
          {datasetName}
        </Typography>
        <Typography sx={{ p: 2 }}>No data available</Typography>
      </StyledPaper>
    );
  }

  return (
    <StyledPaper elevation={3}>
      <Typography variant="h6" sx={{ p: 1, backgroundColor: '#e0e0e0', borderBottom: '1px solid #bdbdbd' }}>
        {datasetName}
      </Typography>
      <TableContainer sx={{ maxHeight: 440, overflowY: 'auto' }}>
        <Table stickyHeader size="small" aria-label={`${datasetName} table`}>
          <TableHead>
            <TableRow>
              {headers.map((header) => (
                <StyledTableCell 
                  key={header} 
                  sx={{ fontWeight: 'bold', backgroundColor: '#f0f0f0' }}
                  sortDirection={orderBy === header ? order : false}
                >
                  <TableSortLabel
                    active={orderBy === header}
                    direction={orderBy === header ? order : 'asc'}
                    onClick={() => handleSort(header)}
                  >
                    {header}
                  </TableSortLabel>
                </StyledTableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
          {sortedData.map((row, index) => (
            <StyledTableRow key={index} hover>
              {headers.map((header) => (
                <StyledTableCell key={`${index}-${header}`}>
                  {row[header]}
                </StyledTableCell>
              ))}
            </StyledTableRow>
          ))}
          </TableBody>
        </Table>
      </TableContainer>
    </StyledPaper>
  );
};

export default DatasetTable;
