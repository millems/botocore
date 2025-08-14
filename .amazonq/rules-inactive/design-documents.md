# Feature Design Document Guidance

## Description

This guidance document provides a structured framework for creating effective Feature Design Documents at Amazon. It is intended for technical document authors 
(L4-L7 in the SDE job family) who are designing and implementing customer-facing features. A well-crafted Feature Design Document serves as a blueprint for
implementation, a reference for decision-making, and a communication tool for stakeholders.

The target audience for this guidance is technical writers and engineers responsible for documenting feature designs. The documents produced following this 
guidance are primarily intended for technical teams implementing the features, as well as product managers, technical program managers, and other stakeholders 
involved in feature development.

Source material: https://w.amazon.com/bin/view/ASBX/Learn/SystemDesign/SampleDocs/

## DOs

### Document Structure and Organization
- Begin with a concise executive summary (1 paragraph) that captures the feature's purpose, value proposition, and key decision points
- Include a clear problem statement supported by quantitative data (metrics, customer feedback, etc.)
- Organize content in a logical hierarchy with descriptive section headings
- Use a consistent structure across all feature design documents
- Limit the main document to 6 pages, using appendices for supporting details
- Include a table of contents for documents longer than 3 pages

### Problem Definition and Context
- Clearly articulate the customer problem being solved with specific examples
- Provide relevant context and background information
- Include metrics that demonstrate the impact of the problem
- Connect the feature to broader business goals and customer needs
- Define success metrics that will be used to evaluate the feature's impact
- Explain how the current solution (if any) falls short

### Technical Design and Implementation
- Include architecture diagrams showing how the feature integrates with existing systems
- Present at least 2-3 alternative approaches with consistent evaluation criteria
- Clearly explain the rationale behind the chosen solution
- Document both functional and non-functional requirements
- Address cross-cutting concerns (security, performance, scalability, etc.)
- Include sequence diagrams for complex interactions
- Provide API specifications when applicable

### Implementation Planning and Operations
- Break down implementation into logical phases or milestones with clear timelines
- Document dependencies on other teams, services, or features
- Include a comprehensive testing strategy covering unit, integration, and end-to-end tests
- Detail the rollout plan, including any phased deployment or experimentation strategy
- Define operational metrics and alerting thresholds
- Include runbooks for common operational tasks and troubleshooting
- Address capacity planning considerations

## DON'Ts

### Document Structure Mistakes
- Write lengthy, unfocused executive summaries that bury the lead
- Include excessive background information before stating the problem
- Use vague section headings that don't clearly indicate content
- Create deep nesting of sections that makes the document hard to navigate
- Include "TBD" or incomplete sections in final documents
- Omit a clear statement of what the document is asking from readers

### Problem Definition Pitfalls
- Present solutions without clearly defining the problem first
- Rely on anecdotal evidence instead of data to justify the feature
- Focus solely on technical challenges without connecting to customer impact
- Define problems too broadly or too narrowly
- Assume readers understand the context without explanation
- Omit success metrics or ways to measure impact

### Technical Design Flaws
- Present only one solution without considering alternatives
- Include excessive implementation details that will quickly become outdated
- Use technical jargon without explanation
- Create diagrams without clear labels or explanations
- Omit consideration of edge cases and error scenarios
- Focus only on happy path scenarios
- Neglect non-functional requirements like performance and security

### Implementation Planning Gaps
- Provide vague timelines without specific milestones
- Omit dependencies on other teams or systems
- Create unrealistic implementation plans that don't account for constraints
- Neglect operational considerations like monitoring and alerting
- Fail to address how the feature will be tested
- Omit rollout and rollback strategies
- Ignore capacity planning and scaling considerations

## Examples

### Good Example 1: Executive Summary

```
## Executive Summary

This document proposes a new "Past Purchases View" feature that allows customers to quickly reorder previously purchased items. Based on customer feedback and usage data, we've identified that 68% of repeat customers struggle to find previously purchased items, resulting in reduced repeat purchase rates. The proposed solution adds a dedicated "Past Purchases" tab to the main navigation, with intelligent sorting based on purchase frequency and recency. This approach was selected over alternatives because it provides the most direct access with minimal UI changes, can be implemented within one sprint, and is expected to increase repeat purchase rate by 12-15% based on A/B testing results.
```

### Good Example 2: Problem Statement with Data

```
## 2. Problem Statement

### 2.1 Customer Impact
Analysis of customer behavior shows that 68% of repeat customers attempt to search for previously purchased items, but only 37% successfully complete a repeat purchase. Customer feedback indicates three primary pain points:

1. Difficulty remembering exact product names (mentioned in 72% of related feedback)
2. Inability to quickly access purchase history (mentioned in 65% of feedback)
3. Challenges in distinguishing between similar products they've purchased before (mentioned in 48% of feedback)

### 2.2 Business Impact
This friction in the repeat purchase flow results in:
- 23% lower repeat purchase rate compared to industry benchmarks
- Estimated $3.2M in lost annual revenue
- 15% higher customer support contacts related to order history questions

### 2.3 Current Solution Limitations
The current approach requires customers to navigate to their account, find the orders section, locate the specific order, and then find the product - a process requiring 5-7 clicks. User testing shows this flow has an 82% abandonment rate.
```

### Good Example 3: Technical Design with Alternatives

```
## 3. Design Alternatives

We considered three approaches to solving the past purchases discovery problem:

### 3.1 Alternative 1: Past Purchases Tab (Recommended)
Add a dedicated "Past Purchases" tab to the main navigation.

**Pros:**
- Direct access with minimal clicks (1-2)
- Maintains consistent navigation pattern
- Can be implemented within one sprint
- Supports intelligent sorting algorithms

**Cons:**
- Adds another top-level navigation item
- Limited space for additional metadata

### 3.2 Alternative 2: Enhanced Search Integration
Prioritize previously purchased items in search results.

**Pros:**
- No UI changes required
- Leverages existing search behavior

**Cons:**
- Only helps customers who remember to search
- Requires complex search algorithm changes
- Difficult to communicate the feature to customers

### 3.3 Alternative 3: Account Section Enhancement
Redesign the account orders section for easier reordering.

**Pros:**
- Keeps purchase history in expected location
- Comprehensive order context available

**Cons:**
- Still requires 3-4 clicks to access
- Maintains the fundamental navigation issues
- Requires significant redesign of account pages

**Decision:** We selected Alternative 1 because it provides the most direct access with minimal UI changes, can be implemented quickly, and directly addresses the primary customer pain point of quick access to purchase history.
```

### Good Example 4: Implementation Plan

```
## 5. Implementation Plan

### 5.1 Development Phases

#### Phase 1: Core Functionality (Sprint 22.1)
- Create backend API for retrieving past purchases with sorting options
- Implement basic UI for Past Purchases tab
- Add product card components with essential information
- Implement basic sorting (recency)

#### Phase 2: Enhanced Features (Sprint 22.2)
- Add intelligent sorting algorithms based on purchase frequency
- Implement filtering capabilities
- Add quick reorder functionality
- Integrate with recommendations service for "similar items"

#### Phase 3: Optimization (Sprint 22.3)
- Implement performance optimizations
- Add caching layer for frequent users
- Implement A/B testing framework for sorting algorithms
- Add telemetry for feature usage

### 5.2 Dependencies
- Requires Product Catalog Service API enhancements (Team Alpha, committed for Sprint 21.3)
- Needs Order History Service access (Team Beta, already available)
- UI Component Library updates (Team Gamma, scheduled for Sprint 21.3)

### 5.3 Testing Strategy
- Unit tests for all new components and services
- Integration tests for API interactions
- End-to-end tests for complete purchase flows
- A/B testing to validate impact on repeat purchase rate
- Usability testing with 5-7 customers per iteration
```

### Bad Example 1: Vague Executive Summary

```
## Executive Summary

This document is about adding a new feature to help customers find things they bought before. Customers have trouble finding products they purchased previously, so we want to make it easier for them. We're planning to add something to the UI that will show past purchases. This should help customers buy things again more easily. We think this will be good for business and make customers happier.
```

### Bad Example 2: Problem Statement Without Data

```
## Problem Statement

Customers can't easily find products they've purchased before. This is frustrating for them and probably causes us to lose sales. The current way of finding past purchases is not very good. We should make it better so customers can reorder things more easily.
```

### Bad Example 3: Single Solution Without Alternatives

```
## Design

We will add a Past Purchases tab to the main navigation. This will show all the products the customer has bought before. They can click on items to buy them again. This is the best solution for this problem.
```

### Bad Example 4: Vague Implementation Plan

```
## Implementation Plan

We will build this feature in the next few sprints. First we'll do the backend work, then the frontend. We'll need help from some other teams. We should test it to make sure it works correctly. Once it's ready, we'll release it to customers.
```

## Rationale

### Document Structure and Organization

1. **Concise executive summary**: A focused summary ensures busy stakeholders can quickly grasp the essence of the feature and make informed decisions without reading the entire document.

2. **Clear problem statement with data**: Quantitative data demonstrates the significance of the problem and justifies the investment in solving it, aligning with Amazon's data-driven culture.

3. **Logical hierarchy with descriptive headings**: Well-organized content with clear headings improves readability and allows readers to quickly locate specific information, respecting their time.

4. **Consistent structure**: Standardized document formats create familiarity, allowing readers to quickly navigate and find information across different feature documents.

5. **Six-page limit with appendices**: Forcing conciseness ensures the document focuses on the most important information while still providing access to supporting details, aligning with Amazon's six-pager tradition.

6. **Table of contents**: Navigation aids help readers quickly find relevant sections in longer documents, improving the reading experience.

### Problem Definition and Context

1. **Clear problem articulation**: Specific examples help readers understand the real-world impact of the problem, connecting technical solutions to customer needs.

2. **Relevant context**: Background information ensures all readers have the necessary context to understand the problem and proposed solution, regardless of their prior knowledge.

3. **Impact metrics**: Quantifying the problem's impact demonstrates its significance and provides a baseline for measuring improvement, supporting data-driven decision making.

4. **Connection to business goals**: Linking features to broader objectives ensures alignment with company strategy and helps prioritize development efforts.

5. **Success metrics**: Defining how success will be measured ensures accountability and provides clear criteria for evaluating the feature's effectiveness.

6. **Current solution limitations**: Understanding the shortcomings of existing approaches helps justify the need for a new solution and informs design decisions.

### Technical Design and Implementation

1. **Architecture diagrams**: Visual representations help readers quickly understand complex systems and how the new feature integrates with existing components.

2. **Alternative approaches**: Presenting multiple options demonstrates thorough analysis and helps stakeholders understand the trade-offs involved in the chosen solution.

3. **Solution rationale**: Explaining the reasoning behind decisions helps build consensus and provides context for future reference.

4. **Comprehensive requirements**: Documenting both functional and non-functional requirements ensures all aspects of the feature are considered during implementation.

5. **Cross-cutting concerns**: Addressing security, performance, and scalability early prevents these critical aspects from being overlooked.

6. **Sequence diagrams**: Visual representations of complex interactions improve understanding of dynamic behavior and help identify potential issues.

7. **API specifications**: Clear interface definitions ensure proper integration and reduce misunderstandings during implementation.

### Implementation Planning and Operations

1. **Phased implementation**: Breaking work into logical phases creates manageable chunks and allows for incremental delivery and feedback.

2. **Dependency documentation**: Clearly identifying dependencies helps manage risks and coordinate work across teams.

3. **Comprehensive testing strategy**: Defining how the feature will be tested ensures quality and reduces the risk of defects reaching production.

4. **Detailed rollout plan**: Planning the deployment strategy in advance reduces risks and ensures smooth delivery to customers.

5. **Operational metrics**: Defining what to monitor helps quickly identify issues in production and measure the feature's performance.

6. **Runbooks**: Documenting operational procedures ensures consistent handling of incidents and reduces mean time to recovery.

7. **Capacity planning**: Considering resource requirements in advance prevents performance issues as usage scales.
