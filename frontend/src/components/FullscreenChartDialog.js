import React from 'react';
import { Dialog, DialogContent, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const FullscreenChartDialog = ({ open, handleClose, chart }) => {
  return (
    <Dialog fullScreen open={open} onClose={handleClose}>
      <DialogContent>
        <IconButton
          edge="end"
          color="inherit"
          onClick={handleClose}
          aria-label="close"
          sx={{ position: 'absolute', right: 8, top: 8 }}
        >
          <CloseIcon />
        </IconButton>
        {chart}
      </DialogContent>
    </Dialog>
  );
};

export default FullscreenChartDialog;