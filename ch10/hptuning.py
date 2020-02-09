# Initialize search space
# Initialize model
while not objective_reached and not bugdget_exhausted:
  # Obtain new hyperparameters
  suggestion = GetSuggestions()
  
  # Run trial with new hyperparameters; collect metrics
  metrics = RunTrial(suggestion)
  
  # Report metrics
  Report(metrics)
