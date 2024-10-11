import React, { useState } from 'react';
import { Paper, Typography, List, ListItem, ListItemText, Divider, IconButton } from '@mui/material';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import FullscreenChartDialog from './FullscreenChartDialog';

const PreviousInsights = ({ insights }) => {
  const [fullscreenChart, setFullscreenChart] = useState(null);

  const handleOpenFullscreen = (chart) => {
    setFullscreenChart(chart);
  };

  const handleCloseFullscreen = () => {
    setFullscreenChart(null);
  };

  return (
    <>
      <Paper elevation={3} sx={{ p: 2, mt: 2 }}>
        <Typography variant="h6" gutterBottom>Previous Insights</Typography>
        <List>
          {insights.map((item, index) => (
            <React.Fragment key={index}>
              <ListItem alignItems="flex-start">
                <ListItemText
                  primary={`Query: ${item.query}`}
                  secondary={
                    <>
                      <Typography component="span" variant="body2" color="text.primary">
                        Date: {item.date}
                      </Typography>
                      <div style={{ marginTop: 8, height: 100, backgroundColor: '#f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
                        Chart Placeholder
                        <IconButton
                          sx={{ position: 'absolute', right: 8, top: 8 }}
                          onClick={() => handleOpenFullscreen(item.chart)}
                        >
                          <FullscreenIcon />
                        </IconButton>
                      </div>
                    </>
                  }
                />
              </ListItem>
              {index < insights.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      </Paper>
      <FullscreenChartDialog
        open={!!fullscreenChart}
        handleClose={handleCloseFullscreen}
        chart={fullscreenChart}
      />
    </>
  );
};

export default PreviousInsights;