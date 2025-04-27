#!/bin/bash
# filepath: /home/users/bjiang/hpc-project/scripts/Run-Tests.sh

# Parse command line arguments
INSTALL_METHOD=${1:-"local"}  # Default to easybuild if no argument provided

# Validate installation method using pattern matching with an array
valid_methods=("local" "easybuild" "eessi" "all")
if [[ ! " ${valid_methods[@]} " =~ " ${INSTALL_METHOD} " ]]; then
    echo "ERROR: Invalid installation method. Use 'local', 'easybuild', 'eessi', or 'all'"
    echo "Usage: $0 [local|easybuild|eessi|all]"
    exit 1
fi

# Setup logging
LOG_DIR="$HOME/hpc-project/log"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/test_run.log"

echo "Starting HPC benchmark test suite at $(date)" | tee -a "$LOG_FILE"
echo "Installation method: $INSTALL_METHOD" | tee -a "$LOG_FILE"
echo "=======================================" | tee -a "$LOG_FILE"

# Path definitions
SCRIPT_DIR="$HOME/hpc-project/scripts"
INSTALL_SCRIPT="$SCRIPT_DIR/1.Install-OSU-Micro-Benchmarks.sh"
TEST_SCRIPT="$SCRIPT_DIR/3.New-Tests.sh"

# Check if scripts exist
if [ ! -f "$INSTALL_SCRIPT" ]; then
    echo "ERROR: Install script not found at $INSTALL_SCRIPT" | tee -a "$LOG_FILE"
    exit 1
fi

if [ ! -f "$TEST_SCRIPT" ]; then
    echo "ERROR: Test script not found at $TEST_SCRIPT" | tee -a "$LOG_FILE"
    exit 1
fi

# Make scripts executable
chmod +x "$INSTALL_SCRIPT" "$TEST_SCRIPT"

# Function to run tests for a specific method
run_test_for_method() {
    local method="$1"
    echo "=======================================" | tee -a "$LOG_FILE"
    echo "Running tests for method: $method" | tee -a "$LOG_FILE"
    echo "=======================================" | tee -a "$LOG_FILE"
    
    # Define consistent environment file name
    local env_file="/tmp/osu_env_${method}.sh"
    
    # Step 1: Run the installation script with method
    echo "Installing OSU benchmarks ($method)..." | tee -a "$LOG_FILE"
    "$INSTALL_SCRIPT" --method "$method" | tee -a "$LOG_FILE"
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        echo "ERROR: Installation script failed for $method" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # Step 2: Source the environment file
    if [ -f "$env_file" ]; then
        echo "Sourcing environment file: $env_file" | tee -a "$LOG_FILE"
        source "$env_file"
    else
        echo "Warning: Environment file not found at $env_file" | tee -a "$LOG_FILE"
        echo "Continuing with existing environment" | tee -a "$LOG_FILE"
    fi
    
    # Step 3: Verify environment is ready
    if [ -z "$EBROOTOSUMINMICROMINBENCHMARKS" ]; then
        echo "Warning: EBROOTOSUMINMICROMINBENCHMARKS not set, attempting to load modules directly" | tee -a "$LOG_FILE"
        case "$method" in
            "easybuild")
                module load tools/EasyBuild/5.0.0 2>/dev/null
                module load perf/OSU-Micro-Benchmarks/7.5-gompi-2023b 2>/dev/null
                ;;
            "eessi")
                module load EESSI 2>/dev/null
                module load OSU-Micro-Benchmarks/7.2-gompi-2023b 2>/dev/null
                ;;
            "local")
                echo "Using local OSU installation" | tee -a "$LOG_FILE"
                ;;
        esac
    fi
    
    # Step 4: Run the test script
    echo "Running benchmark tests for $method..." | tee -a "$LOG_FILE"
    echo "---------------------------------------" | tee -a "$LOG_FILE"
    export OSU_METHOD="$method"  # Make method available to test script
    "$TEST_SCRIPT" | tee -a "$LOG_FILE"
    local test_exit_code=${PIPESTATUS[0]}
    
    # Step 5: Report results for this method
    if [ $test_exit_code -eq 0 ]; then
        echo "✅ Tests completed successfully for $method" | tee -a "$LOG_FILE"
    else
        echo "❌ Tests completed with errors for $method (exit code: $test_exit_code)" | tee -a "$LOG_FILE"
    fi
    
    return $test_exit_code
}

# Initialize overall exit code
OVERALL_EXIT_CODE=0

# Run tests based on selected method
if [ "$INSTALL_METHOD" = "all" ]; then
    # Run tests for each method
    METHODS=("local" "easybuild" "eessi")
    for method in "${METHODS[@]}"; do
        run_test_for_method "$method"
        METHOD_EXIT_CODE=$?
        
        # Keep track of errors
        if [ $METHOD_EXIT_CODE -ne 0 ]; then
            OVERALL_EXIT_CODE=$METHOD_EXIT_CODE
        fi
        
        # Add some separation between test runs
        echo "" | tee -a "$LOG_FILE"
        echo "---------------------------------------" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
    done
else
    # Run only the specified method
    run_test_for_method "$INSTALL_METHOD"
    OVERALL_EXIT_CODE=$?
fi

# Final summary
echo "=======================================" | tee -a "$LOG_FILE"
if [ $OVERALL_EXIT_CODE -eq 0 ]; then
    echo "✅ All test runs completed successfully" | tee -a "$LOG_FILE"
else
    echo "❌ One or more test runs had errors" | tee -a "$LOG_FILE"
fi

echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "Completed at: $(date)" | tee -a "$LOG_FILE"

exit $OVERALL_EXIT_CODE